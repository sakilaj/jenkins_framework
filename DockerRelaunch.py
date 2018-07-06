# Docker Relaunch will call scripts
#   docker_load.sh
#   docker_delete.sh
#   PropertyFileMgmt_ContainerCreation.py
#       This scripts inturn call docker_create.sh
#   StartContainerServices.py
# Removed/commented "release_version = '08_004'" as its causing image load on every major release ans also same is done in script docker_load.sh also

import os
import sys
import json

# To Check for the argument
print "---------------------------------------------------------------------------------"

node = sys.argv[1]
with open('config.ini') as fh:
    data = json.load(fh)
    #print "---------------------------------------------------------------------------------"
    docker_image = data['node'][node]['docker_image']
    #print "Docker Image Name    : ",docker_image
    cmd = ("echo %s | cut -d'_' -f2,3")%docker_image
    card = os.system(cmd)
    card = os.popen(cmd).read()
    print "card                 : ",card
    docker_name = data['node'][node]['docker_container_name']
    #print "Docker Name          : ",docker_name
    sig_cardid = ("echo %s | cut -d '-' -f3")%docker_name
    cardid = os.system(sig_cardid)
    idd = os.popen(sig_cardid).read()
    print "cardid               : ",idd

if len(sys.argv) < 2:
    print 'Requires Node name to start relaunch script'
    exit()
else:
    print sys.argv[:]
    node = sys.argv[1]

#To check for build model
release_version = '09_000'

with open('config.ini') as fh:
    data = json.load(fh)

try:
    docker_container_name = data['node'][node]["docker_container_name"]
except KeyError:
    print "The container key sent does not exist in the config file"
    exit()

if node == 'PTMSG' or node == 'EGLS':
    build = data['node'][node]["docker_load_name"]
if node == 'XCAP' or node == 'WCSR':
    build = data['node'][node]["docker_load_name"]
else:
    build = sys.argv[1]

print '\n'
#print "Container name to be launched is ",docker_container_name
print '\n'
#print '\n',node, ' is being Relaunched'
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


#Script takes comments of the card name in CAPS, for example for poc its "POC"
print "Docker Load script STARTED for %s " %(card)
os.system('sh docker_load.sh %s' %(card))
print "Docker Load script FINISHED for %s " %(card)
#Script does not take any comments
#python EMSRLSScript.py (No need)

print "Docker Delete script STARTED for %s" %(card)
#Delete the container with the below script
os.system('sh docker_delete.sh %s' %(idd))
print "Docker delete script FINISHED %s" %(card)
print ""

os.system('sleep 1')
#os.system('docker rmi a107a8c4aca0')
#os.system('sleep 10')

print "Docker create script STARTED %s" %(node)
#Script to get property file, edit file and use the file to create the container
os.system('python PropertyFileMgmt_ContainerCreation1.py %s %s' %(node,card))
print "Docker create script FINISHED %s" %(node)

#os.system('sleep 20')

#print "Start container service STARTED \n \n"
#To start container service
#os.system('python StartContainerServices.py %s' %node)
#print "Start container service FINISHED \n \n"

print "Execution completed"
print "---------------------------------------------------------------------------------"
exit(0)
