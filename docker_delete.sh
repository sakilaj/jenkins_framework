#!/bin/bash
#Takes docker name as argument,
#ex. 
LOGFILE=/DGlogs/container_launch.log
release_tag=""
echo "---------------------------------------------------------------------------------"
release_tag=`docker ps -a | grep $1 | awk 'NF>1{print $NF}'`
echo "Deleting $release_tag ..."
rm_kodiak_container.sh -a DELETE $release_tag >> $LOGFILE 2>&1
echo "Deleting $release_tag ...Done"
echo ""
echo "Triggering Launch..."
exit 0
