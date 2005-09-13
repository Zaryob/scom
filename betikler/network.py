#!/usr/bin/python
# -*- coding: utf-8 -*-

import array
import fcntl
import struct
import socket
import sys

class ifconfig:
    """ ioctl stuff """

#   From <bits/ioctls.h>

    # Socket configuration controls
    SIOCGIFNAME = 0x8910        # get iface name
    SIOCSIFLINK = 0x8911        # set iface channel
    SIOCGIFCONF = 0x8912        # get iface list
    SIOCGIFFLAGS = 0x8913       # get flags
    SIOCSIFFLAGS = 0x8914       # set flags
    SIOCGIFADDR = 0x8915        # get PA address
    SIOCSIFADDR = 0x8916        # set PA address
    SIOCGIFDSTADDR  = 0x8917    # get remote PA address
    SIOCSIFDSTADDR  = 0x8918    # set remote PA address
    SIOCGIFBRDADDR  = 0x8919    # get broadcast PA address
    SIOCSIFBRDADDR  = 0x891a    # set broadcast PA address
    SIOCGIFNETMASK  = 0x891b    # get network PA mask
    SIOCSIFNETMASK  = 0x891c    # set network PA mask
    SIOCGIFMETRIC = 0x891d      # get metric
    SIOCSIFMETRIC = 0x891e      # set metric
    SIOCGIFMEM = 0x891f         # get memory address (BSD)
    SIOCSIFMEM = 0x8920         # set memory address (BSD)
    SIOCGIFMTU = 0x8921         # get MTU size
    SIOCSIFMTU = 0x8922         # set MTU size
    SIOCSIFNAME = 0x8923        # set interface name
    SIOCSIFHWADDR = 0x8924      # set hardware address
    SIOCGIFENCAP = 0x8925       # get/set encapsulations
    SIOCSIFENCAP = 0x8926
    SIOCGIFHWADDR = 0x8927      # Get hardware address
    SIOCGIFSLAVE = 0x8929       # Driver slaving support
    SIOCSIFSLAVE = 0x8930
    SIOCADDMULTI = 0x8931       # Multicast address lists
    SIOCDELMULTI = 0x8932
    SIOCGIFINDEX = 0x8933       # name -> if_index mapping
    SIOGIFINDEX = SIOCGIFINDEX  # misprint compatibility :-)
    SIOCSIFPFLAGS = 0x8934      # set/get extended flags set
    SIOCGIFPFLAGS = 0x8935
    SIOCDIFADDR = 0x8936        # delete PA address
    SIOCSIFHWBROADCAST = 0x8937 # set hardware broadcast addr
    SIOCGIFCOUNT = 0x8938       # get number of devices

    SIOCGIFBR = 0x8940          # Bridging support
    SIOCSIFBR = 0x8941          # Set bridging options
    SIOCGIFTXQLEN = 0x8942      # Get the tx queue length
    SIOCSIFTXQLEN = 0x8943      # Set the tx queue length


    # ARP cache control calls
    SIOCDARP = 0x8953       # delete ARP table entry
    SIOCGARP = 0x8954       # get ARP table entry
    SIOCSARP = 0x8955       # set ARP table entry

    # RARP cache control calls
    SIOCDRARP = 0x8960      # delete RARP table entry
    SIOCGRARP = 0x8961      # get RARP table entry
    SIOCSRARP = 0x8962      # set RARP table entry


    # Driver configuration calls
    SIOCGIFMAP = 0x8970     # Get device parameters
    SIOCSIFMAP = 0x8971     # Set device parameters


    # DLCI configuration calls
    SIOCADDDLCI = 0x8980   # Create new DLCI device
    SIOCDELDLCI = 0x8981   # Delete DLCI device


#   From <net/if.h>    

    IFF_UP = 0x1           # Interface is up.
    IFF_BROADCAST = 0x2    # Broadcast address valid.
    IFF_DEBUG = 0x4        # Turn on debugging.
    IFF_LOOPBACK = 0x8     # Is a loopback net.
    IFF_POINTOPOINT = 0x10 # Interface is point-to-point link.
    IFF_NOTRAILERS = 0x20  # Avoid use of trailers.
    IFF_RUNNING = 0x40     # Resources allocated.
    IFF_NOARP = 0x80       # No address resolution protocol.
    IFF_PROMISC = 0x100    # Receive all packets.
    IFF_ALLMULTI = 0x200   # Receive all multicast packets.
    IFF_MASTER = 0x400     # Master of a load balancer.
    IFF_SLAVE = 0x800      # Slave of a load balancer.
    IFF_MULTICAST = 0x1000 # Supports multicast.
    IFF_PORTSEL = 0x2000   # Can set media type.
    IFF_AUTOMEDIA = 0x4000 # Auto media select active.


    def __init__(self):
        # create a socket to communicate with system
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _ioctl(self, func, args):
        return fcntl.ioctl(self.sockfd.fileno(), func, args)

    def _getaddr(self, ifname, func):
        ifreq = (ifname + '\0'*32)[:32]
        try:
            result = self._ioctl(func, ifreq)
        except IOError:
            return None

        return socket.inet_ntoa(result[20:24])

    def getInterfaceList(self):
        """ Get all interface names in a list """
        # get interface list
        buffer = array.array('c', '\0' * 1024)
        ifconf = struct.pack("iP", buffer.buffer_info()[1], buffer.buffer_info()[0])
        result = self._ioctl(self.SIOCGIFCONF, ifconf)

        # loop over interface names
        iflist = []
        size, ptr = struct.unpack("iP", result)
        for idx in range(0, size, 32):
            ifconf = buffer.tostring()[idx:idx+32]
            name, dummy = struct.unpack("16s16s", ifconf)
            name, dummy = name.split('\0', 1)
            iflist.append(name)

        return iflist

    def getFlags(self, ifname):
        """ Get the flags for an interface """
        ifreq = (ifname + '\0'*32)[:32]
        try:
            result = self._ioctl(self.SIOCGIFFLAGS, ifreq)
        except IOError:
            return 0

        # extract the interface's flags from the return value
        flags, = struct.unpack('H', result[16:18])

        # return "UP" bit
        return flags

    def getAddr(self, ifname):
        """ Get the inet addr for an interface """
        return self._getaddr(ifname, self.SIOCGIFADDR)

    def getMask(self, ifname):
        """ Get the netmask for an interface """
        return self._getaddr(ifname, self.SIOCGIFNETMASK)

    def getBroadcast(self, ifname):
        """ Get the broadcast addr for an interface """
        return self._getaddr(ifname, self.SIOCGIFBRDADDR)

    def isUp(self, ifname):
        """ Check whether interface is UP """
        return (self.getFlags(ifname) & self.IFF_UP) != 0

class route:
    """ ioctl stuff """

#   From <bits/ioctls.h>

    # Routing table calls
    SIOCADDRT = 0x890B      # add routing table entry
    SIOCDELRT = 0x890C      # delete routing table entry
    SIOCRTMSG = 0x890D      # call to routing system

#   From <net/route.h>

    RTF_UP = 0x0001         # Route usable
    RTF_GATEWAY = 0x0002    # Destination is a gateway

    RTF_HOST = 0x0004       # Host entry (net otherwise)
    RTF_REINSTATE = 0x0008  # Reinstate route after timeout
    RTF_DYNAMIC = 0x0010    # Created dyn. (by redirect)
    RTF_MODIFIED = 0x0020   # Modified dyn. (by redirect)
    RTF_MTU = 0x0040        # Specific MTU for this route
    RTF_MSS = RTF_MTU       # Compatibility
    RTF_WINDOW = 0x0080     # Per route window clamping
    RTF_IRTT = 0x0100       # Initial round trip time
    RTF_REJECT = 0x0200     # Reject route
    RTF_STATIC = 0x0400     # Manually injected route
    RTF_XRESOLVE = 0x0800   # External resolver
    RTF_NOFORWARD = 0x1000  # Forwarding inhibited
    RTF_THROW = 0x2000      # Go to next class
    RTF_NOPMTUDISC = 0x4000 # Do not send packets with DF


if __name__ == "__main__":
    ifc = ifconfig()
    ifaces = ifc.getInterfaceList()
    
    for name in ifaces:
        print "%s is %s ip %s netmask %s broadcast %s" % (name, ('DOWN', 'UP')[ifc.isUp(name)],
            ifc.getAddr(name), ifc.getMask(name), ifc.getBroadcast(name))

