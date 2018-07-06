#!/bin/bash

#Prerequisites
 
#Takes CARD NAME as a parameter in Capital letters ex. {POC, XDMS, WEB, etc} and loads the docker image 
#Takes build version as the second argument ex. {09_000}
card=$1
echo "CARD              : $card"
EMS_IP=192.168.28.112
echo "EMS_IP            : $EMS_IP"
BUILD_RELEASE_IP=10.0.16.83
echo "BUILD_RELEASE_IP  : $BUILD_RELEASE_IP"
BUILD_SERVER_IP=10.0.29.121
echo "BUILD_SERVER_IP   : $BUILD_SERVER_IP"
#DAT_FILE_DIR=/home/kodiak
#echo "DAT_FILE_DIR      : $DAT_FILE_DIR"
VM_IP=192.168.28.111
echo "VM_IP             : $VM_IP"

# Declaring alias instead of function to sshpass for ssh and scp
alias sshssh='sshpass -p kodiak ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no  -o LogLevel=error -tt'
alias sshscp='sshpass -p kodiak scp -q -o StrictHostKeyChecking=no -o CheckHostIP=no -o LogLevel=error'

# DAT file copy and initialization
sshssh kodiak@"$BUILD_RELEASE_IP" "cd /home/kodiak/ITG; ls -ltr KPTT_09_000_00_X64-CP_*-MCS* | tail -n 1" </dev/null >new_dat_file
#sshssh kodiak@"$BUILD_RELEASE_IP" "cd /NAS-INDIA/Release9.0/Docker/; ls -ltr KPTT_09_000_00_X64-CP_*-MCS* | tail -n 1" </dev/null >new_dat_file
DAT_FILE_NAME=`cat new_dat_file | tail -n 1 | awk '{print$9}'`
echo "DAT_FILE_NAME     : $DAT_FILE_NAME"
FILE=/home/kodiak/`cat new_dat_file | tail -n 1 | awk '{print$9}'`
echo "FILE              : $FILE"

#if [ -e "$FILE" ]; then
    sshscp -p kodiak@"$BUILD_RELEASE_IP":"/home/kodiak/ITG/KPTT_09_000_00_X64-CP_*-MCS*" /home/kodiak/
    #sshscp -p kodiak@"$BUILD_RELEASE_IP":"/NAS-INDIA/Release9.0/Docker/KPTT_09_000_00_X64-CP_*-MCS*" /home/kodiak/
    sshscp -p /home/kodiak/KPTT_09_000_00_X64-CP_*-MCS* root@"$EMS_IP":"/home/kodiak/"
    #sshscp -p /home/kodiak/KPTT_09_000_00_X64-CP_*-MCS* root@"$EMS_IP":"/home/kodiak/"
    sshscp -p /DGdata/Scripts/docker_ems.sh root@"$EMS_IP":"/home/kodiak/"
    echo "Triggering EMS to configure input_file.dat for $card ..."
    sshssh root@"$EMS_IP" "sh /home/kodiak/docker_ems.sh $card" </dev/null
    echo "Triggering Image load from Docker Registry..."
    echo "./kodiakVM_Reg_Config_Pull_Images.py input_file.dat pull"
    sshssh root@"$EMS_IP" "cd /DG/activeRelease/container/os-playbook; ./kodiakVM_Reg_Config_Pull_Images.py input_file.dat pull"
    echo ""
    echo "Image for $card is loaded as below..."
    docker images | egrep -i *_$1\ 
#else
    #echo "Exit on Error: File $FILE not found in $VM_IP."
#    exit 1
#fi
