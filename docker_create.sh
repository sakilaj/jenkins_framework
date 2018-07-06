#!/bin/bash
# Should pass properties file to establich connection
#create_kodiak_container.sh -f $1
echo $1
/usr/local/bin/create_kodiak_container.sh -c -f $1
