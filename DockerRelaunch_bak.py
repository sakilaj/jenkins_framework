# Docker Relaunch will call scripts
#   docker_load.sh
#   docker_delete.sh
#   PropertyFileMgmt_ContainerCreation.py
#       This scripts inturn call docker_create.sh
#   StartContainerServices.py

import os
import sys
import json

# To Check for the argument
if len(sys.argv) < 2:
    print 'Requires Node name to start relaunch script'
    exit()
else:
    print sys.argv[:]
    node = sys.argv[1]

#To check for build model
#release_version = '08_004'
if node == 'XCAP' or node == 'WCSR':
    build = 'WEB'
else:
    build = sys.argv[1]

with open('config.ini') as fh:
    data = json.load(fh)
#print data
try:
    docker_container_name = data['node'][node]["docker_container_name"]
except KeyError:
    print "The container key sent does not exist in the config file"
    exit()

print '\n \n', node, ' is being Relaunched'
print 'Container name to be launched is ', docker_container_name, '\n \n'

#Steps followed for update
#1. Copy Loads to /DGdata/Loads in VM machine #Execute in host VM
#2.  Run docker load -i IMAGE #Execute in host VM
#3.  perl /DG/activeRelease/SetContainerRLFlag.pl #Execute on EMS
#4.  Copy the properties file from /DG/activeRelease/container/conf/nodeip_timestamp.properties in VM /home/autoinstall/temp/
#5.  Edit the properties file by changing the image name. #Execute in VM host
#6.  Run rm_kodiak_container.sh -a DELETE PROJECT-NODENAME-PTTSERVID #Execute on VM host
#7.  Run create_kodiak_container.sh -f nodeip_timestamp.properties #Execute on VM host
#8.  Copy the latest /DG/activeRelease/container/conf/nodeip_timestamp.properties from EMS node to kodiak@node_IP:
#9.  Run perl /DG/activeRelease/Tools/POCContainerConfig.pl /home/kodiak/nodeip_timestamp.properties #Execute in node subjected to upgrade
#10. Check for systemctl status kodiakDG.service #Execute in node subjected to upgrade


#Script docker_load.sh covers step 1 & 2
#Script takes comments of the card name in CAPS, for example for poc its "POC"
print "Docker Load script STARTED \n \n"
os.system('sh docker_load.sh %s' %(build))
print "Docker Load script FINISHED \n \n"

#Script EMSRLSScript.py covers step 3
#Script does not take any comments
#python EMSRLSScript.py (No need)

print "Docker delete script STARTED \n \n"
#Delete the container with the below script
os.system('sh docker_delete.sh %s' %(docker_container_name))
print "Docker delete script FINISHED\n \n"

os.system('sleep 10')

print "Docker create script STARTED \n \n"
#Script to get property file, edit file and use the file to create the container
os.system('python PropertyFileMgmt_ContainerCreation.py %s' %node)
print "Docker create script FINISHED \n \n"

os.system('sleep 20')

print "Start container service STARTED \n \n"
#To start container service
os.system('python StartContainerServices.py %s' %node)
print "Start container service FINISHED \n \n"

print "Execution completed"
