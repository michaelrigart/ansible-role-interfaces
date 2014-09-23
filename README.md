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


Role Variables
--------------

The variables that can be passed to this role and a brief description about
them are as follows:

    # The list of ethernet interfaces to be added to the system
    network_ether_interfaces: []

    # The list of bridge interfaces to be added to the system
    network_bridge_interfaces: []

    # The list of bonded interfaces to be added to the system
    network_bond_interfaces: []

Note: The values for the list are listed in the examples below.

1) Configure eth1 and eth2 on a host with a static IP and a dhcp IP. Also
define static routes and a gateway.

    - hosts: myhost
      roles:
        - role: network
          network_ether_interfaces:
           - device: eth1
             bootproto: static
             address: 192.168.1.150
             netmask: 255.255.255.0
             gateway: 192.168.1.1
             network: 192.168.1.1
             dns-servers: 8.8.8.8 8.8.4.4
             dns-search: myhost.com
             
             route:
              - network: 192.168.200.0
                netmask: 255.255.255.0
                gateway: 192.168.1.1
              - network: 192.168.100.0
                netmask: 255.255.255.0
                gateway: 192.168.1.1
           - device: eth2
             bootproto: dhcp

2) Configure a bridge interface with multiple NIcs added to the bridge.

    - hosts: myhost
      roles:
        - role: network
          network_bridge_interfaces:
           -  device: br1
              type: bridge
              address: 192.168.1.150
              netmask: 255.255.255.0
              bootproto: static
              stp: "on"
              ports: [eth1, eth2]

Note: Routes can also be added for this interface in the same way routes are
added for ethernet interfaces.

3) Configure a bond interface with an "active-backup" slave configuration.

    - hosts: myhost
      roles:
        - role: network
          network_bond_interfaces:
            - device: bond0
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

4) Configure a bonded interface with "802.3ad" as the bonding mode and IP
address obtained via DHCP.

    - hosts: myhost
      roles:
        - role: network
          network_bond_interfaces:
            - device: bond0
              bootproto: dhcp
              bond_mode: 802.3ad
              bond_miimon: 100
              bond_slaves: [eth1, eth2]

5) All the above examples show how to configure a single host, The below
example shows how to define your network configurations for all your machines.

Assume your host inventory is as follows:

### /etc/ansible/hosts

    [dc1]
    host1
    host2

Describe your network configuration for each host in host vars:

### host_vars/host1

    network_ether_interfaces:
           - device: eth1
             bootproto: static
             address: 192.168.1.150
             netmask: 255.255.255.0
             gateway: 192.168.1.1
             route:
              - network: 192.168.200.0
                netmask: 255.255.255.0
                gateway: 192.168.1.1
    network_bond_interfaces:
            - device: bond0
              bootproto: dhcp
              bond_mode: 802.3ad
              bond_miimon: 100
              bond_slaves: [eth2, eth3]

### host_vars/host2

    network_ether_interfaces:
           - device: eth0
             bootproto: static
             address: 192.168.1.150
             netmask: 255.255.255.0
             gateway: 192.168.1.1

Create a playbook which applies this role to all hosts as shown below, and run
the playbook. All the servers should have their network interfaces configured
and routed updated.

    - hosts: all
      roles:
        - role: network

Note: Ansible needs network connectivity throughout the playbook process, you
may need to have a control interface that you do *not* modify using this
method so that Ansible has a stable connection to configure the target
systems.


Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: MichaelRigart.interfaces }

License
-------

GPLv3

Author Information
------------------

Michaël Rigart <michael@netronix.be>