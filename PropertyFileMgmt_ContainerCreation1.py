import paramiko
import os
import re
import subprocess
import sys
import json

node = sys.argv[1]
with open('config.ini') as fh:
    data = json.load(fh)
print "---------------------------------------------------------------------------------"
emsIP = data['node']['EMS']['docker_ip']
print "EMS IP               : ",emsIP
containerIP = data['node'][node]['docker_ip'] 
print "Container IP         : ",containerIP
card_name = data['node'][node]['docker_image_name']
print "Card Name            : ",card_name
docker_name = data['node'][node]['docker_container_name']
print "Docker Name          : ",docker_name
docker_load_name = data['node'][node]['docker_load_name']
print "Docker LOAD Name     : ",docker_load_name
docker_image = data['node'][node]['docker_image']
print "Docker Image Name    : ",docker_image

#Method to define largest tagid

def large_tag_id(filename):
    cmd = ['docker', 'images', '|', 'grep', '-i','%s' %(card_name), '|', 'awk', "{'print$2'}"]
    print "cmd:",cmd
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    print "proc:", proc
    out = [j[0] for j in [i.split('\n') for i in proc.stdout.readlines()]]
    print "out:", out
    largest_tag_id = str(sorted([str(i) for i in out])[-1])
    print "largest_tag_id       : ",largest_tag_id
    with open('%s'%(file_name), 'r') as fh:
        line_list = fh.readlines()
        for j in [i.split('=') for i in line_list]:
            if j[0] == 'IMAGE':
                image_with_tag_id = j[1].split('\n')[0]
            else:
                pass
            if j[0] == 'MEMORY_LIMIT':
                memoryLimitValue = j[1].strip('\n')
                new_memoryLimitValue = memoryLimitValue+'M'
                #print "image_with_tag_id    : ",image_with_tag_id
    image_tag_id_list = (image_with_tag_id.split(':')[0].split('/')[1], image_with_tag_id.split(':')[1])
    return (image_tag_id_list,largest_tag_id,memoryLimitValue,new_memoryLimitValue,image_with_tag_id)

def SSH_EMS(host,username,password,cmd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,username=username,password=password)
    stdin,stdout,stderr = ssh.exec_command(cmd)
    out_list = []
    for line in stdout:
        out_list.append(line.strip('\n'))
    ssh.close()
    return out_list

#To select the recent updated properties file and extact the file name
cmd_propertyList = ['ls', '-lrt', '/home/autoinstall/jenkins/']
tmp1 = subprocess.Popen(cmd_propertyList, stdout=subprocess.PIPE)
property_file_name = tmp1.stdout.readlines()[-1].split(' ')[-1].split('\n')[0]
file_name = '/home/autoinstall/jenkins/%s' %(property_file_name)
print "property_file_name   : ",property_file_name
#print "file_name:", file_name

#First to find the largest tagid
image_tag_id_list = large_tag_id(file_name)

#signaling card ID
sig_cardid = ("echo %s | cut -d '_' -f2 | cut -d '-' -f1")%docker_name
cardid = os.system(sig_cardid)
card = os.popen(sig_cardid).read()
print "cardid               : ",card

#print property_file
image_tag = str(image_tag_id_list[1])
#print "final_image  :",final_image
cmd = "source /etc/kodiakEMS.conf; /DG/activeRelease/Tools/DBScripts/ttdir EMSDSN \"update DG.CONTAINER_CONFIGVALUES set PARAMVALUE='rhel74_platform/%s:%s' where PARAMNAME='IMAGE' and PARAMVALUE like '%%%s%%';exit\"" %(docker_image,image_tag,card_name)
print ""
print "Updating EMS DB for latest IMAGE..." 
print cmd
print ""
out = SSH_EMS(emsIP,'root','kodiak',cmd)
print "Status...",out

cmd = "sh /DG/activeRelease/container/scripts/ansible-trigger.sh 1 %s" %card
print "Triggering EMS for container Launch..."
out = SSH_EMS(emsIP,'root','kodiak',cmd)
print "Status...",out

#To check if the created container is created successfully
load = sys.argv[2]
print ""
print "Service check for    : "
docker_name_cmd = ("docker ps -a | grep -i %s: | awk 'NF>1{print $NF}'")%load
docker_cmd = os.system(docker_name_cmd)
out = os.popen(docker_name_cmd).read()
print "Status...",out
status = ("systemctl status %s")%out
stat = os.system(status)

#print "Service check %s" %(docker_name)
#cmd = ['systemctl', 'status', '%s' %(out), '|', 'grep', 'Active', '|', 'awk', "{'print $1$2'}"]
#print "cmd: ", cmd
#proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
#print "proc: ", proc
#process_output = proc.stdout.readlines()[2].split(' ')
#print "process_output: ", process_output
#print ' '.join(process_output)

#To check if the process is Active or Dead

#if process_output[4] == 'active' and process_output[5] == '(running)':
#    print "The launch of the container is successfull"
#    os.system('systemctl status %s >> container_launch_status' %(docker_name))
#elif process_output[4] == 'dead':
#    print 'The launch of the container is unsuccessfull'
#    os.system('systemctl status %s >> container_launch_status' %(docker_name))
#else:
#    print "Container launch status unknown"


print "---------------------------------------------------------------------------------"
print "<<< Summary >>>"
