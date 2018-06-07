# Copyright (c) 2017 StackHPC Ltd.

import re

import jinja2


def _fail(reason):
    return {
        "diff": True,
        "reason": reason,
    }


def _pass():
    return {"diff": False}


def _device(interface):
    """Return the device associated with an interface."""
    return interface["device"]


def _fact_name(device):
    """Return the name of the Ansible fact associated with an interface."""
    # Ansible fact names replace dashes and colons with an underscore.
    return "ansible_%s" % re.sub(r"[\-\:]", "_", device)


def _fact(context, device):
    """Return the fact associated with an interface."""
    fact_name = _fact_name(device)
    return context[fact_name]


def _interface_check(context, interface, interface_type=None):
    """Check whether the active state of an Ethernet interface is as requested.

    :param context: Jinja2 context.
    :param interface: An item in interfaces_ether_interfaces.
    :param interface_type: The expected interface type.
    :returns: A dict containing 'diff' and 'reason' items.
    """
    device = _device(interface)

    # Existence
    fact_name = _fact_name(device)
    if fact_name not in context:
        return _fail("Interface %s does not exist" % device)

    fact = _fact(context, device)

    # Interfaces with a colon (:) in their name are subinterfaces - effectively
    # secondary IP addresses on another interface.
    if ':' not in device:
        # State
        if not fact.get("active"):
            return _fail("Interface %s is not active" % device)

        # Type
        if interface_type:
            fact_type = fact["type"]
            if interface_type != fact_type:
                return _fail("Interface %s is of an unexpected type" % device)

    # Static IPv4 address
    if interface.get("bootproto") == "static" and interface.get("address"):
        fact_address = fact.get("ipv4", {}).get("address")
        secondaries = fact.get("ipv4_secondaries", None)
        if interface["address"] != "0.0.0.0":
            # IP address
            if not fact_address:
                if not secondaries:
                    return _fail("Interface %s has no IPv4 address" % device)
                else:
                    for address_dict in secondaries:
                        if interface['address'] == address_dict['address']:
                            fact['ipv4'] = address_dict
                            fact_address = address_dict['address']
                            break
            if fact_address != interface["address"]:
                return _fail("Interface %s has incorrect IPv4 address" % device)

            # Netmask
            if (interface.get("netmask") and
                    fact["ipv4"]["netmask"] != interface["netmask"]):
                return _fail("Interface %s has incorrect IPv4 netmask" % device)

            # Gateway
            if interface.get("gateway"):
                fact_gateway = context.get("ansible_default_ipv4", {}).get("gateway")
                if not fact_gateway:
                    return _fail("Default IPv4 gateway is missing")
                if interface["gateway"] != fact_gateway:
                    return _fail("Default IPv4 gateway is incorrect")

        elif fact_address:
            return _fail("Interface %s has an IPv4 address but none was "
                         "requested" % device)
    
    # Static IPv6 address
    if interface.get("bootproto") == "static" and interface.get("ip6"):
        fact_address = fact.get("ipv6", [])
        # IP address
        if len(fact_address) == 0:
            return _fail("Interface %s has no IPv6 address" % device)
        
        for item in fact_address:
            if item["address"] == interface["ip6"]["address"] and item["prefix"] == str(interface["ip6"]["prefix"]):
                break
        else:
            return _fail("Interface %s has incorrect IPv6 address" % device)
        
        # Gateway
        if interface["ip6"].get("gateway"):
            fact_gateway = context.get("ansible_default_ipv6", {}).get("gateway")
            if not fact_gateway:
                return _fail("Default IPv6 gateway is missing")
            if interface["ip6"]["gateway"] != fact_gateway:
                return _fail("Default IPv6 gateway is incorrect")

    # MTU
    if interface.get("mtu"):
        fact_mtu = fact.get("mtu")
        if interface["mtu"] != fact_mtu:
            return _fail("Interface %s has incorrect MTU" % device)

    return _pass()


@jinja2.contextfilter
def ether_check(context, interface):
    """Check whether the active state of an Ethernet interface is as requested.

    :param context: Jinja2 context.
    :param interface: An item in interfaces_ether_interfaces.
    :returns: A dict containing 'diff' and 'reason' items.
    """
    result = _interface_check(context, interface, "ether")
    return result


@jinja2.contextfilter
def bridge_check(context, interface):
    """Check whether the active state of a bridge interface is as requested.

    :param context: Jinja2 context.
    :param interface: An item in interfaces_ether_interfaces.
    :returns: A dict containing 'diff' and 'reason' items.
    """
    result = _interface_check(context, interface, "bridge")
    if result["diff"]:
        return result

    device = _device(interface)
    fact = _fact(context, device)

    # Bridge ports
    fact_ports = fact.get("interfaces", [])
    interface_ports = interface.get("ports", [])
    missing = set(interface_ports) - set(fact_ports)
    if missing:
        return _fail("Bridge interface %s has missing ports: %s" %
                     (device, ", ".join(missing)))

    for port in interface_ports:
        port_interface = {"device": port}
        result = _interface_check(context, port_interface)
        if result["diff"]:
            return result

    return result


@jinja2.contextfilter
def bond_check(context, interface):
    """Check whether the active state of a bond interface is as requested.

    :param context: Jinja2 context.
    :param interface: An item in interfaces_ether_interfaces.
    :returns: A dict containing 'diff' and 'reason' items.
    """
    result = _interface_check(context, interface, "bonding")
    if result["diff"]:
        return result

    device = _device(interface)
    fact = _fact(context, device)

    # Bond mode
    if interface.get("bond_mode"):
        fact_mode = fact["mode"]
        # Convert numerical modes to the named modes presented by ansible.
        mode_lookup = {
            "1": "active-backup",
            "2": "balance-xor",
            "3": "broadcast",
            "4": "802.3ad",
            "5": "balance-tlb",
            "6": "balance-alb",
        }
        interface_mode = str(interface["bond_mode"])
        interface_mode = mode_lookup.get(interface_mode, interface_mode)
        if interface_mode != fact["mode"]:
            return _fail("Bond interface %s has incorrect bond mode" % device)

    # Bond miimon
    if interface.get("bond_miimon"):
        fact_miimon = fact["miimon"]
        if str(interface["bond_miimon"]) != fact["miimon"]:
            return _fail("Bond interface %s has incorrect miimon" % device)

    # Bond slaves
    fact_slaves = fact.get("slaves", [])
    interface_slaves = interface.get("bond_slaves", [])
    missing = set(interface_slaves) - set(fact_slaves)
    if missing:
        return _fail("Bond interface %s has missing slaves: %s" %
                     (device, ", ".join(missing)))
    additional = set(fact_slaves) - set(interface_slaves)
    if additional:
        return _fail("Bond interface %s has additional slaves: %s" %
                     (device, ", ".join(additional)))

    for slave in interface_slaves:
        slave_interface = {"device": slave}
        result = _interface_check(context, slave_interface, "ether")
        if result["diff"]:
            return result

    return result


class FilterModule(object):
    """Interface comparison filters."""

    def filters(self):
        return {
            'ether_check': ether_check,
            'bridge_check': bridge_check,
            'bond_check': bond_check,
        }
