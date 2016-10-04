#!/usr/bin/env python
# Get CDP neighbors on interfaces and create description to apply to the interface

from pysnmp.entity.rfc3413.oneliner import cmdgen
import argparse
import paramiko
import os
import pwd
import getpass
import re

parser = argparse.ArgumentParser(description='Update interface descriptions based on CDP information')
parser.add_argument('-c', '--community', help='community string',
        action='store',
        type=str,
        required=True)
parser.add_argument('-f', '--hostsfile', help='filename',
	action='store',
	type=str,
	default='hostfile.txt')
args =  parser.parse_args()

inputargs = args.hostsfile
community = args.community

def get_username():
    return pwd.getpwuid(os.getuid()).pw_name

def get_password():
    return getpass.getpass()

# Open file and read content line by line. Every line should be 1 switch.
def get_list_of_switches():
    inputfile = open(inputargs, 'r')
    return inputfile

def get_cdp_neighbours():
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
                 cmdgen.CommunityData(community),
                 cmdgen.UdpTransportTarget((host, 161)),
                 0,
                 25,
                 (1,3,6,1,4,1,9,9,23,1,2,1,1,6),
            )
    return varBindTable

def get_cdp_interfaces():
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
                 cmdgen.CommunityData(community),
                 cmdgen.UdpTransportTarget((host, 161)),
                 0,
                 25,
                 (1,3,6,1,4,1,9,9,23,1,2,1,1,7),
            )
    return varBindTable

def get_all_local_interfaces():
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
                 cmdgen.CommunityData(community),
                 cmdgen.UdpTransportTarget((host, 161)),
                 0,
                 25,
                 (1,3,6,1,2,1,31,1,1,1,1),
            )
    return varBindTable

def get_all_current_descriptions():
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
                 cmdgen.CommunityData(community),
                 cmdgen.UdpTransportTarget((host, 161)),
                 0,
                 25,
                 (1,3,6,1,2,1,31,1,1,1,18),
            )
    return varBindTable

def get_cdp_entries():
    """Word als eerst uitgevoerd als je het script runt"""

    cdp_neighbours = get_cdp_neighbours()
    cdp_interfaces = get_cdp_interfaces()
    all_local_interfaces = get_all_local_interfaces()
    all_current_descriptions = get_all_current_descriptions()

    cdp_entries = {}

    # Retrieve CDP hostnames
    for neighbour in cdp_neighbours:
        for name, value in neighbour:
            ifindex = name.prettyPrint().rsplit('.', 2)[1]
            cdp_entries[ifindex] = {'remote_host': value.prettyPrint()}

    # Retrieve CDP interfaces
    for interface in cdp_interfaces:
        for name, value in interface:
            ifindex = name.prettyPrint().rsplit('.', 2)[1]
            cdp_entries[ifindex]['remote_interface'] = value.prettyPrint()

    # Retrieve local interfaces and match with CDP entries
    for local_interface in all_local_interfaces:
        for name, value in local_interface:
            ifindex = name.prettyPrint().rsplit('.', 1)[1]
            if ifindex in cdp_entries:
                cdp_entries[ifindex]['local_interface'] = value.prettyPrint()

    # Retrieve current descriptions and match with CDP entries
    for current_description in all_current_descriptions:
        for name, value in current_description:
            ifindex = name.prettyPrint().rsplit('.', 1)[1]
            if ifindex in cdp_entries:
                cdp_entries[ifindex]['current_description'] = value.prettyPrint()

    return cdp_entries

def copy_configuration_to_switch():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
      paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    channel = client.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')
    
    stdin.write('''
    show version
    dir
    show inventory
    exit
    ''')
    print stdout.read()

#def prepare_switch_config():
#    with open('interface_configuration.txt') as input_data:
#         for line in input_data:
#             if line.strip() starts with 'switchname':
#                break
#        
#         for line in input_data:
#             if line.strip() starts with '==================================':
#                break
#             print line

    


if __name__ == '__main__':
  # Start with retrieving username and password
  username = get_username()
  password = get_password()

  f=open("interface_configuration.txt","w") # This is file with all configuration changes
  list_of_switches = get_list_of_switches()
  for host in list_of_switches:
    print(host)
    f.write("switchname " + host + "\n")

    for ifindex, values in get_cdp_entries().items():
            f.write("interface " + (values["local_interface"] + "\n"))
            f.write("! old_description " + (values["current_description"] + "\n"))
            f.write("description -= " + (values["remote_host"] + " " + values["remote_interface"] + " =-" + "\n" + "\n"))
    f.write("==============================\n")
    copy_configuration_to_switch()
  f.close()
