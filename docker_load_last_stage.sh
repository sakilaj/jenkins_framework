#!/bin/bash

#Prerequisites
 
#Takes CARD NAME as a parameter in Capital letters ex. {POC, XDMS, WEB, etc} and loads the docker image 
#Takes build version as the second argument ex. {08_003}
# Changed grep $2 for failure in jenkins launch on every major release
card=$1
echo "CARD              : $card"
EMS_IP=192.168.28.112
echo "EMS_IP            : $EMS_IP"
BUILD_RELEASE_IP=10.0.16.83
echo "BUILD_RELEASE_IP  : $BUILD_RELEASE_IP"
BUILD_SERVER_IP=10.0.29.121
echo "BUILD_SERVER_IP   : $BUILD_SERVER_IP"

# Declaring alias instead of function to sshpass for ssh and scp
alias sshssh='sshpass -p kodiak ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no  -o LogLevel=error -tt'
alias sshscp='sshpass -p kodiak scp -q -o StrictHostKeyChecking=no -o CheckHostIP=no -o LogLevel=error'

# DAT file copy and initialization
#EMS_INPUT_FILE=`sshssh root@"$EMS_IP" "ls /DG/activeRelease/container/os-playbook/input_file.dat"` </dev/null
#echo "EMS_INPUT_FILE    : $EMS_INPUT_FILE"
sshssh kodiak@"$BUILD_RELEASE_IP" "cd /NAS-INDIA/Release9.0/Docker/; ls -ltr KPTT_09_000_00_X64-DG_*-MCS* | tail -n 1" </dev/null >new_dat_file
NEW_DAT_FILE_NAME=`cat new_dat_file | tail -n 1 | awk '{print$9}'`
echo "NEW_DAT_FILE_NAME : $NEW_DAT_FILE_NAME"

sshscp -p kodiak@"$BUILD_RELEASE_IP":"/NAS-INDIA/Release9.0/Docker/KPTT_09_000_00_X64-DG_*-MCS*" /home/kodiak/
sshscp -p /home/kodiak/KPTT_09_000_00_X64-DG_*-MCS* root@"$EMS_IP":"/home/kodiak/"

sshssh root@"$EMS_IP" "grep -i IMAGE_NAME_FILE: /DG/activeRelease/container/os-playbook/input_file.dat | head -n 1 | cut -d':' -f2" </dev/null >old_dat_file
OLD_DAT_FILE_NAME=`cat old_dat_file`
echo "OLD_DAT_FILE_NAME : $OLD_DAT_FILE_NAME"


sshssh root@"$EMS_IP" "sed -i '/IMAGE_NAME_FILE/c\'IMAGE_NAME_FILE:"$NEW_DAT_FILE_NAME" /DG/activeRelease/container/os-playbook/input_file.dat" </dev/null
sshssh root@"$EMS_IP" "grep -i IMAGE_NAME_FILE: /DG/activeRelease/container/os-playbook/input_file.dat | head -n 1" </dev/null >current_dat_file
CURRENT_DAT_FILE_NAME=`cat current_dat_file | cut -d':' -f2`
echo "CURRENT_DAT_FILE  : "$CURRENT_DAT_FILE_NAME

# Loading image using Docker registry

sshssh root@"$EMS_IP" "cat `ls -ltr /home/kodiak/KPTT_09_000_00_X64-DG_*-MCS* | tail -n 1 | awk '{print $9}'` | egrep -i $card"  </dev/null >image_name
IMAGE_NAME=`cat image_name`
echo "IMAGE_NAME        : $IMAGE_NAME"
sshssh root@"$EMS_IP" "echo $IMAGE_NAME >/DGdata/Loads/$NEW_DAT_FILE_NAME"

#sshssh root@"$EMS_IP" "cd /DG/activeRelease/container/os-playbook; ./kodiakVM_Reg_Config_Pull_Images.py input_file.dat pull"
echo ""
echo "Image for $card is loaded as below..."
docker images | grep -i $card
