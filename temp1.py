import paramiko
import os
import re
import subprocess
import sys
import json

node = sys.argv[1]
with open('config_tmp.ini') as fh:
    data = json.load(fh)
print "---------------------------------------------------------------------------------"
emsIP = data['node']['EMS']['docker_ip']
print "EMS IP : ", emsIP
containerIP = data['node'][node]['docker_ip']
print "Container IP : ", containerIP
card_name = data['node'][node]['docker_image_name']
print "Card Name : ", card_name
docker_name = data['node'][node]['docker_container_name']
print "Docker Name : ", docker_name
docker_load_name = data['node'][node]['docker_load_name']
print "Docker laod Name : ", docker_load_name
docker_image = data['node'][node]['docker_image']
print "Docker Image : ", docker_image


update = {data['node'][node]['docker_container_name']["PROJ-WDS_16-011261-R9.0_D3_31"]}
load = json.loads(update)
#data['node'][node]['docker_container_name']="PROJ-WDS_16-011261-R9.0_D3_31"
#json.dump(data)
with open("config_tmp.ini","w") as f:
    json.dump(load,f)
f.close()
