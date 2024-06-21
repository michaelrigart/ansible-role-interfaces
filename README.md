Ansible Interfaces Role
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

# An optional filter parameter to pass to the setup module.
interfaces_setup_filter: "{{ omit }}"

# An optional gather_subset parameter to pass to the setup module.
interfaces_setup_gather_subset: "{{ omit }}"

# An option to merge all configurations setup with merge: true
# in the global interfaces file (Debian-Family only)
interfaces_merge: false
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
         pre_up: sleep 5
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

4) Configure a bonded interface with "802.3ad" as the bonding mode, specify the
802.3ad aggregation selection logic to use the aggregator with largest aggregate
bandwidth, and IP address obtained via DHCP.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_bond_interfaces:
        - device: bond0
          bootproto: dhcp
          bond_mode: 802.3ad
          bond_ad_select: bandwidth
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

6) Configure a hot-pluggable Wifi interface `wlan0` with a static IP and a
`wpa_supplicant` configuration. Also configure eth0 with a dhcp IP.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
        - device: wlan0
          allowclass: allow-hotplug
          bootproto: static
          address: 192.168.1.150
          netmask: 255.255.255.0
          network: 192.168.1.0
          broadcast: 192.168.1.255
          gateway: 192.168.1.1
          dnsnameservers: 192.168.1.1
          wpaconf: /etc/wpa_supplicant/wpa_supplicant.conf
        - device: eth0
          bootproto: dhcp
```

7) Configure a static IPv4 address, route along with an IPv6 address and route on an interface.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
        - device: ens160
          bootproto: static
          address: 10.99.99.2
          netmask: 255.255.255.0
          route:
            - network: 10.99.98.0
              netmask: 255.255.255.0
              gateway: 10.99.99.1
          ip6:
            address: fd49:f9f5:ccb4:2acd::ac18:1002
            prefix: 120
            route:
              - network: 64:FF9B::/96
                gateway: fd49:f9f5:ccb4:2acd::ac18:1001
```

8) All the above examples show how to configure a single host, The below
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

9) CentOS 8 cloud image workaround

CentOS 8 cloud images ship with ifcfg files for ens3 and eth0. ifcfg-ens3 seems
to be a relic from the image build process, and causes the network service to
fail. ifcfg-eth0 is useful for most virtual machines, but if a cloud image is
deployed on bare metal and eth0 is absent, the network service will fail. This
role will by default remove these files, if there is no such interface on the
system, and no such interface is specified in the role variables.

This workaround is configured via `interfaces_workaround_centos_remove`. To
set a different interface file to remove:

```yaml
interfaces_workaround_centos_remove:
  - eth1
```

Or to avoid performing this workaround:

```yaml
interfaces_workaround_centos_remove: []
```

10) Allowed addresses

Sometimes it may be useful to not immediately assign an IP address to an
interface, but to allow another process to assign one. An example use case is a
virtual IP address dynamically added or by a process such as keepalived.
This may be configured via an `allowed_addresses` field in an Ethernet, bond or
bridge interface configuration.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
        - device: eth0
          bootproto: static
          address: 0.0.0.0
          allowed_addresses:
            - 10.0.0.2
```

11) Custom options for static routes

Adding custom options to static routes is possible via the `options` attribute,
which should be a list.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
        - device: eth0
          bootproto: static
          address: 0.0.0.0
          route:
           - network: 192.168.200.0
             netmask: 255.255.255.0
             gateway: 192.168.1.1
             options:
               - onlink
               - metric 400
```

12) Configure an IPoIB (infiniband) interface

Configuring an IPoIB interface is possible using `type: ipoib` when defining the interface.

**WARNING: You can configure the ip address and routes for an IPoIB interface but other functionalities like vlans are not supported in infiniband networks**

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
        - device: eth0
          bootproto: static
          address: 192.168.1.150
          netmask: 255.255.255.0
          gateway: 192.168.1.1
        - device: ib0
          bootproto: static
          address: 10.10.1.10
          netmask: 255.255.255.0
          type: ipoib
```

13) Configure ethtool options (RedHat-family only)

Setting ethtool options on an interface is possible using the `ethtool_opts`
attribute, which should be a string. For example, this can be used to set RX/TX
ring parameters. This is only supported on distributions of the RedHat family.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_ether_interfaces:
        - device: eth0
          bootproto: static
          address: 192.168.1.150
          netmask: 255.255.255.0
          gateway: 192.168.1.1
          ethtool_opts: "-G ${DEVICE} rx 8192 tx 8192"
```

To apply ethtool options to bond slaves or bridge ports, set the attribute on
the bond or bridge itself. Setting different options per underlying interface
is not supported at this time.

14) Configure firewalld zones (RedHat-family only)

  Adding interface to firewalld zone is possible using the `zone` attribute.
  This is only supported on distributions of the RedHat family.

  ```yaml
 - hosts: myhost
   roles:
     - role: MichaelRigart.interfaces
       interfaces_ether_interfaces:
         - device: eth0
           bootproto: static
           address: 192.168.1.150
           netmask: 255.255.255.0
           gateway: 192.168.1.1
           zone: trusted
 ```

15) Pause to wait for interfaces to become active

On some OS distributions (including Ubuntu), it may be necessary to wait after
bouncing network interfaces before they are active. This can be done by setting
``interfaces_pause_time`` to a number of seconds to delay.

16) Configure HW(MAC) address for interface

  Configuring interface HW adrress is possible using the `hwaddr` attribute.
  This alone may not be sufficient to change MAC from default one, however
  specifying hw address is necessary for some systems.

```yaml
 - hosts: myhost
   roles:
     - role: MichaelRigart.interfaces
       interfaces_ether_interfaces:
         - device: eth0
           bootproto: static
           address: 192.168.1.150
           netmask: 255.255.255.0
           gateway: 192.168.1.1
           hwaddr: 00:11:22:33:44:55
```

17) Configure HW(MAC) address for bonded/bridged interface

  Configuring interface HW adrress is possible using the `hwaddr` attribute.

```yaml
- hosts: myhost
  roles:
    - role: MichaelRigart.interfaces
      interfaces_bond_interfaces:
        - device: bond0
          bootproto: dhcp
          bond_mode: 802.3ad
          hwaddr: 00:11:22:33:44:55
      interfaces_bridge_interfaces:
       -  device: br1
          type: bridge
          bootproto: dhcp
          hwaddr: 00:11:22:33:44:66
          ports: [eth1, eth2]
```

18) Routes and rules can be a mix of strings and hashes (a.k.a. dict, mapping, associative array, etc.) allowing
    the role to handle rules and routes outside the expected formats. These can also be applied to loopback devices in
    distributions using Network Manager's new `nmconnect` configuration files (e.g. RHEL8 & RHEL9).

    The example below configures an interface, to act as a second interface so that any traffic that hits it is returned via the same interface. In addition internal traffic is marked so it can be picked up by some other service (like HAproxy).

### host_vars/proxy1
```yaml
interfaces_route_tables:
    - name: frontend
      id: 200
    - name: marktable
      id: 100
interfaces_ether_interfaces:
    - device: eth1
      bootproto: static
      address: 10.10.10.1
      netmask: 255.255.255.0
      defroute: false
      route:
        - table: frontend
          device: eth1
          network: 0.0.0.0
          netmask: 0.0.0.0
          gateway: 10.10.10.254
      rules:
        - from: 10.10.10.1
          table: frontend
        - "fwmark 1 lookup marktable"
    - device: lo
      type: loopback
      # Setting bootproto to dhcp is required to set `method=auto` in the nmconnect file
      # This replicates `ip route add local 0.0.0.0/0 dev lo table 100"`
      bootproto: dhcp
      route:
        - table: marktable
          device: lo
          network: 0.0.0.0
          netmask: 0
          options:
            - type: local
```

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
