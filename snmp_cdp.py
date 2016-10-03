#!/usr/bin/env python

# Get CDP neighbors on interfaces and create description to apply to the interface

#from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

errorIndication, errorStatus, errorIndex, \
varBindTable = cmdgen.CommandGenerator().bulkCmd(  
            cmdgen.CommunityData('test123'),  
            cmdgen.UdpTransportTarget(('172.16.1.212', 161)),  
            0,   
            25,  
            (1,3,6,1,4,1,9,9,23,1,2,1,1,6),
            (1,3,6,1,4,1,9,9,23,1,2,1,1,7),
		(1,3,6,1,2,1,31,1,1,1,1),
       )

# For every row in table find out which interface this is, get the remote interface and the local interface
for varBindTableRow in varBindTable:
#    for name, val in varBindTableRow:
#            #s_local =  % (name.prettyPrint(), val.prettyPrint())
#            print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
#            #print '%s' % (name.prettyPrint())
#	    #print " {} {} ".format(name.prettyPrint().rsplit(".", 2), val.prettyPrint())
    for name, val in varBindTableRow:
      name = name.prettyPrint()
      if name.startswith( 'SNMPv2-SMI::enterprises.9.9.23.1.2.1.1.6' ):
       i = name.rsplit(".", 2)
       global interface
       interface = i[1]
       global switchname
       switchname = val.prettyPrint()
      elif name.startswith( 'SNMPv2-SMI::enterprises.9.9.23.1.2.1.1.7.' + interface ):
       global switchinterface
       switchinterface = val.prettyPrint()
       print " {} {} {} ".format(interface, switchname, switchinterface)
      elif name.startswith( 'SNMPv2-SMI::mib-2.31.1.1.1.1.' + interface ):
       global localinterface
       localinterface = val.prettyPrint()
       print " {} {} {} ".format(interface, switchname, switchinterface)
       print " {} ".format(localinterface)
