#!/bin/bash

#Prerequisites
 
#Takes CARD NAME as a parameter in Capital letters ex. {POC, XDMS, WEB, etc} and loads the docker image 
#Takes build version as the second argument ex. {08_003}
# Changed grep $2 for failure in jenkins launch on every major release
card=$1
echo "CARD              : $card"
EMS_IP=192.168.28.112
echo "EMS_IP            : $EMS_IP"
IMAGE_NAME=""

# DAT file copy and initialization
ems_input_file=/DG/activeRelease/container/os-playbook/input_file.dat
echo "ems_input_file    : $ems_input_file"

OLD_DAT_FILE_NAME=`grep -i IMAGE_NAME_FILE: $ems_input_file | head -n 1 | cut -d':' -f2`
echo "OLD_DAT_FILE_NAME : $OLD_DAT_FILE_NAME"

#NEW_DAT_FILE_NAME=`cd /home/kodiak; ls -ltr KPTT_09_000_00_X64-CP_*-MCS* | tail -n 1 | tail -n 1 | awk '{print$9}'`
NEW_DAT_FILE_NAME=`cd /home/kodiak; ls -ltr KPTT_09_000_00_X64-CP_*-MCS* | tail -n 1 | tail -n 1 | awk '{print$9}'`
echo "NEW_DAT_FILE_NAME : $NEW_DAT_FILE_NAME"
#if [ -e "/DGdata/Loads/$NEW_DAT_FILE_NAME" ]; then
    sed -i '/IMAGE_NAME_FILE/c\'IMAGE_NAME_FILE:"$NEW_DAT_FILE_NAME" $ems_input_file 
    CURRENT_DAT_FILE_NAME=`grep -i IMAGE_NAME_FILE: $ems_input_file | head -n 1 | cut -d':' -f2`
    echo "CURRENT_DAT_FILE  : "$CURRENT_DAT_FILE_NAME

    #if [[ "$NEW_DAT_FILE_NAME" == "$CURRENT_DAT_FILE_NAME" ]]; then
        IMAGE_NAME=`cat /home/kodiak/$NEW_DAT_FILE_NAME | grep -i $card: | head -n 1`
        cat /home/kodiak/$NEW_DAT_FILE_NAME | grep -i $card: | head -n 1 | wc -l >image_line
        if [[ `cat image_line` -eq "1" ]]; then
            echo "IMAGE_NAME        : $IMAGE_NAME"
            echo $IMAGE_NAME >/DGdata/Loads/$NEW_DAT_FILE_NAME
            echo "Image to be Loaded:"; cat /DGdata/Loads/$NEW_DAT_FILE_NAME
        else
            echo "Warning : unable to update /DGdata/Loads/$NEW_DAT_FILE_NAME for latest build..."
            echo ""
            exit 1
        fi
            
    #else
        #echo "Exit on Error: found different IMAGE_NAME_FILE entry in $ems_input_file"
        #exit 1
    #fi
#else
    #echo "Exit on Error: File /DGdata/Loads/$NEW_DAT_FILE_NAME not found in $EMS_IP."
    #exit 1
#fi
