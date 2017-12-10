Ansible Interfaces Role [![Build Status](https://travis-ci.org/michaelrigart/ansible-role-interfaces.svg?branch=master)](https://travis-ci.org/michaelrigart/ansible-role-interfaces)
=======================

An ansible role for configuring different network interfaces.

_WARNING: This role can be dangerous to use. If you lose network connectivity
to your target host by incorrectly configuring your networking, you may be
unable to recover without physical access to the machine._

- Ethernet interfaces
- Bridge interfaces
- Bonded interfaces
- Network routes
- IP routing tables
- IP routing rules

Role Variables
--------------

The variables that can be passed to this role and a brief description about
them are as follows:

```yaml
# The list of route tables to be defined
interfaces_route_tables: []

# The list of ethernet interfaces to be added to the system
interfaces_ether_interfaces: []

# The list of bridge interfaces to be added to the system
interfaces_bridge_interfaces: []

# The list of bonded interfaces to be added to the system
interfaces_bond_interfaces: []
```

Note: The values for the list are listed in the examples below.

1) Configure eth1 and eth2 on a host with a static IP and a dhcp IP. Also
define static routes and a gateway.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
       - device: eth1
         bootproto: static
         address: 192.168.1.150
         netmask: 255.255.255.0
         gateway: 192.168.1.1
         dnsnameservers: 192.0.2.1 192.0.2.2
         dnssearch: example.com
         mtu: 9000
         route:
          - network: 192.168.200.0
            netmask: 255.255.255.0
            gateway: 192.168.1.1
          - network: 192.168.100.0
            netmask: 255.255.255.0
            gateway: 192.168.1.1
       - device: eth2
         bootproto: dhcp
```

2) Configure a bridge interface with multiple NICs added to the bridge.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_bridge_interfaces:
       -  device: br1
          type: bridge
          address: 192.168.1.150
          netmask: 255.255.255.0
          bootproto: static
          stp: "on"
          mtu: 1500
          ports: [eth1, eth2]
```

Note: Routes can also be added for this interface in the same way routes are
added for ethernet interfaces.

3) Configure a bond interface with an "active-backup" slave configuration.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_bond_interfaces:
        - device: bond0
          mtu: 9000
          address: 192.168.1.150
          netmask: 255.255.255.0
          bootproto: static
          bond_mode: active-backup
          bond_miimon: 100
          bond_slaves: [eth1, eth2]
          route:
          - network: 192.168.222.0
            netmask: 255.255.255.0
            gateway: 192.168.1.1
```

4) Configure a bonded interface with "802.3ad" as the bonding mode and IP
address obtained via DHCP.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_bond_interfaces:
        - device: bond0
          bootproto: dhcp
          bond_mode: 802.3ad
          bond_miimon: 100
          bond_downdelay: 200
          bond_updelay: 200
          bond_lacp_rate: 1
          bond_xmit_hash_policy: layer3+4
          bond_slaves: [eth1, eth2]
```

5) Configure a routing table `myroutetable`, and an Ethernet interface `eth1`
with an IP routing rule that defines when to use the routing table. It also
configures an IP route on the interface for the `myroutetable` routing table.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_route_tables:
       - name: myroutetable
         id: 42
      interfaces_ether_interfaces:
       - device: eth1
         bootproto: static
         address: 192.168.1.150
         netmask: 255.255.255.0
         dnsnameservers: 192.0.2.1 192.0.2.2
         dnssearch: example.com
         mtu: 9000
         route:
          - network: 192.168.200.0
            netmask: 255.255.255.0
            gateway: 192.168.1.1
            table: myroutetable
         rules:
          - from 192.168.200.0/24 table myroutetable
```

6) All the above examples show how to configure a single host, The below
example shows how to define your network configurations for all your machines.

Assume your host inventory is as follows:

### /etc/ansible/hosts

    [dc1]
    host1
    host2

Describe your network configuration for each host in host vars:

### host_vars/host1

```yaml
interfaces_ether_interfaces:
  - device: eth1
    bootproto: static
    address: 192.168.1.150
    netmask: 255.255.255.0
    gateway: 192.168.1.1
    route:
     - network: 192.168.200.0
       netmask: 255.255.255.0
       gateway: 192.168.1.1
interfaces_bond_interfaces:
  - device: bond0
    mtu: 9000
    bootproto: dhcp
    bond_mode: 802.3ad
    bond_miimon: 100
    bond_slaves: [eth2, eth3]
```

### host_vars/host2

```yaml
interfaces_ether_interfaces:
  - device: eth0
    bootproto: static
    address: 192.168.1.150
    netmask: 255.255.255.0
    gateway: 192.168.1.1
```

Create a playbook which applies this role to all hosts as shown below, and run
the playbook. All the servers should have their network interfaces configured
and routes updated.

```yaml
- hosts: all
  roles:
    - role: MichaelRigart.interfaces
```

Note: Ansible needs network connectivity throughout the playbook process, you
may need to have a control interface that you do *not* modify using this
method so that Ansible has a stable connection to configure the target
systems.


Example Playbook
----------------

```yaml
- hosts: servers
  roles:
     - { role: MichaelRigart.interfaces, become: true }
```
License
-------

GPLv3

Author Information
------------------

Michaël Rigart <michael@netronix.be>
