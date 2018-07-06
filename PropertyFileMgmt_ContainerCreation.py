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

#Method to define largest tagid

def large_tag_id(filename):
    cmd = ['docker', 'images', '|', 'grep', '-i','%s' %(card_name), '|', 'awk', "{'print$2'}"]
    print "------------------------------------"
    #print "cmd:",cmd
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #print "proc:", proc
    out = [j[0] for j in [i.split('\n') for i in proc.stdout.readlines()]]
    #print "out:", out
    largest_tag_id = str(sorted([str(i) for i in out])[-1])
    print "largest_tag_id:",largest_tag_id
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
        #image_with_tag_id = 'localregistry.kodiakitg.com/' + image_with_tag_id
        print "image_with_tag_id:",image_with_tag_id
    image_tag_id_list = (image_with_tag_id.split(':')[0].split('/')[1], image_with_tag_id.split(':')[1])
    return (image_tag_id_list,largest_tag_id,memoryLimitValue,new_memoryLimitValue,image_with_tag_id)

def SSH_Client(host,username,password,cmd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,username=username,password=password)
    stdin,stdout,stderr = ssh.exec_command('sudo %s'%(cmd))
    out_list = []
    for line in stdout:
        out_list.append(line.strip('\n'))
    ssh.close()
    return out_list

def SFTP_Client(host,port,username,password,localpath,filepath):
    transport = paramiko.Transport((host,port))
    transport.connect(username=username,password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.get(filepath,localpath)

    sftp.close()
    transport.close()
    return True


def SSH_EMS(host,username,password,cmd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,username=username,password=password)
    stdin,stdout,stderr = ssh.exec_command(cmd)
#    print stderr
#    print stdout
    out_list = []
    for line in stdout:
        out_list.append(line.strip('\n'))
    ssh.close()
    return out_list

def SFTP_Put(host,port,username,password,localpath,filepath):
    transport = paramiko.Transport((host,port))
    transport.connect(username=username,password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.put(localpath,filepath)

    sftp.close()
    transport.close()
    return True

#def SSH_EMS(cmd):
#    ssh = subprocess.Popen(["ssh -q -o StrictHostKeyChecking=no -o CheckHostIP=no root@192.168.28.112", cmd],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#    result = ssh.stdout.readlines()
#    print result
#    return result

#def SSH_EMS(host,username,password,cmd):
#    ssh = paramiko.SSHClient()
#    ssh.load_system_host_keys()
#    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#    ssh.connect(host, username=username, password=password)
#    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
#    out_list = []
#    for line in ssh_stdout:
#        out_list.append(line.strip('\n'))
#    ssh.close()
#    return out_list

os.system('rm -rf /root/.ssh/known_hosts')
cmd = "ls -lrt /DG/activeRelease/container/conf/ | grep -i %s | awk '{print $9}'" %(containerIP)
#print "cmd:", cmd
out = SSH_Client(emsIP,'autoinstall','kodiak',cmd)
#print "EMSIP:", emsIP
#print "out:", out
property_file = out[-1]
#print "Property File : ", property_file

filepath = '/DG/activeRelease/container/conf/' + property_file
localpath = '/home/autoinstall/jenkins/' + property_file
#print filepath + '\n', localpath
host = emsIP
port = 22
username = 'autoinstall'
password = 'kodiak'

if SFTP_Client(host,port,username,password,localpath,filepath) == True:
    print ""
    print "Transfer completed"
    print "Starting the Service exection"
else:
    print ""
    print "Transfer failed hence exiting further process"
    exit()

#Copy property file contents from EMS to HostVM
os.system('rm -rf /home/autoinstall/temp/*')
os.system("scp autoinstall@%s:/DG/activeRelease/container/conf/%s* /home/autoinstall/temp" %(emsIP,containerIP))

#To select the recent updated properties file and extact the file name
cmd_propertyList = ['ls', '-lrt', '/home/autoinstall/jenkins/']
tmp1 = subprocess.Popen(cmd_propertyList, stdout=subprocess.PIPE)
property_file_name = tmp1.stdout.readlines()[-1].split(' ')[-1].split('\n')[0]
print "property_file_name:", property_file_name
file_name = '/home/autoinstall/jenkins/%s' %(property_file_name)
print "file_name:", file_name

print ""
print "The Properties file name is ", file_name

#To Edit the properties of the image tag id
#First to find the largest tagid
image_tag_id_list = large_tag_id(file_name)
print "image_tag_id_list:",image_tag_id_list
if str(image_tag_id_list[0][1]) == str(image_tag_id_list[1]):
    print ""
    print "The image is already updated and hence not going for upgrade"
    exit_flag = 1
    pass
else:
    #Edit the properties file to replace with tagid
    os.system("sed -i -e 's/%s:%s/%s:%s/g' %s"%(image_tag_id_list[0][0],image_tag_id_list[0][1],docker_image,image_tag_id_list[1],file_name))
    exit_flag = 0

if image_tag_id_list[2] == image_tag_id_list[3]:
    print ""
    print "The MEMORY_LIMIT is already changed"
    exit_flag = 1
    pass
else:
    print ""
    print "Replacing the MEMORY_LIMIT"
    docker_memory = data['node'][node]['docker_memory']
    os.system("sed -i -e 's/MEMORY_LIMIT=%s/MEMORY_LIMIT=%s/g' %s" %(image_tag_id_list[2],docker_memory,file_name))
    exit_flag = 0

if exit_flag == 1:
    exit()
else:
    print ""
    print "Continuing the process"
    print ""
    pass

#Create Container with the property file
#if node != 'CBS':
#    os.system('create_kodiak_container.sh -f %s' %(file_name))
#else:
#    os.system('create_kodiak_container.sh -c -f %s' %(file_name))

#----
#cmd = "ls -lrt /DG/activeRelease/container/conf/ | grep -i %s | awk '{print $9}'" %(containerIP)
#out = SSH_Client(emsIP,'autoinstall','kodiak',cmd)
#property_file = out[-1]


filepath = '/home/autoinstall/' + property_file
localpath = '/home/autoinstall/temp/' + property_file

#---------------

print filepath + '\n', localpath

host = emsIP
port = 22
username = 'autoinstall'
password = 'kodiak'

#if SFTP_Put(emsIP,port,username,password,localpath,filepath) == True:
#    print "Transfer completed %s %s" %(localpath,filepath)
#else:
#    print "Transfer failed hence exiting further process"
#    exit()

#print "Launching %s ~~~  %s" %(property_file,containerIP)

print ("for remote:%s:%s/%s:%s")%(image_tag_id_list[0][0],image_tag_id_list[0][1],docker_image,image_tag_id_list[1])
print "Property_file before sed:", property_file
cmd = "sed -i -e 's/%s:%s/%s:%s/g' /DG/activeRelease/container/conf/%s" %(image_tag_id_list[0][0],image_tag_id_list[0][1],docker_image,image_tag_id_list[1],property_file)
print "emsIP : host;", emsIP, host
out = SSH_EMS(emsIP,'root','kodiak',cmd)
print "out_sed:",out



cmd = "source /etc/kodiakEMS.conf;ttIsql -connStr 'dsn=emsdsn' -e 'update DG.MQ_NODE_INFO set CONFIG_STATUS=0;exit' -v 1"
print "Updating CONFIG_STATUS" 
out = SSH_EMS(emsIP,'root','kodiak',cmd)

#sig_cardid = ['echo', '%s' %(docker_name),  '|', 'cut', '-d', '\'_\'', '-f2', '|', 'cut', '-d', '\'-\'', '-f1']
sig_cardid = ("echo %s | cut -d '_' -f2 | cut -d '-' -f1")%docker_name
#print "sig command : ", sig_cardid
cardid = os.system(sig_cardid)
card = os.popen(sig_cardid).read()
print "cardid:",card
#print "card:",card
#proc_out = subprocess.Popen(sig_cardid, stdout=subprocess.PIPE)
#cardid = j[0] for j in [i.split('\n') for i in proc_out.stdout.readlines()]]
#cmd = "source /etc/kodiakDG.conf;sudo /bin/sh /DG/activeRelease/container/scripts/ansible-trigger.sh  1 %s %s" %(filepath,containerIP) 
#print property_file
final_image = str(image_tag_id_list[4])
print "final_image:",final_image
cmd = "source /etc/kodiakEMS.conf;ttIsql -connStr 'dsn=emsdsn' -e 'update DG.CONTAINER_CONFIGVALUES set PARAMVALUE='%%%s:%%%s' where PARAMNAME='IMAGE' and PARAMVALUE like '%%%s%%';exit' -v 1" %(image_tag_id_list[0][0],image_tag_id_list[1],card_name)
print "Updating image tag..." ,cmd
out = SSH_EMS(emsIP,'root','kodiak',cmd)

cmd1 = "sh /DG/activeRelease/container/scripts/GenerateContConfig.sh %s" %card
cmd = "sh /DG/activeRelease/container/scripts/ansible-trigger.sh 1 %s" %card
#print "cmd:",cmd
print "Triggering EMS..."
out = SSH_EMS(emsIP,'root','kodiak',cmd1)
print "out_Gen_config:",out
out = SSH_EMS(emsIP,'root','kodiak',cmd)
print "out_Ansible_trigger:",out
#property_file = out[-1]


#os.system('rm -rf %s' %(localpath)) 

#To check if the created container is created successfully
#cmd = "systemctl status JENKINS-KPNS-016641 | grep Active | awk '{print $1}''{print $2}'"
docker_name_cmd = ("docker stats --no-stream $(docker ps | awk '{if(NR>1) print $NF}') | grep -i %s | awk '{print$1}'")%docker_load_name
#docker_name_cmd = ['docker', 'ps', '|', 'grep', '%s' %(docker_load_name), '|', 'awk', "{'print$12'}"]
docker_cmd = os.system(docker_name_cmd)
out = os.popen(docker_name_cmd).read()
#proc = subprocess.Popen(docker_name_cmd, stdout=subprocess.PIPE)
#print "command proc:", proc
#out = [j[0] for j in [i.split('\n') for i in proc.stdout.readlines()]]
#print "out:", out
#line2 = ''.join(('"','%s' %out,'"'))
#line3 = re.sub('\'', '', line2)
#line4 = re.sub('\[', '', line3)
#line5 = re.sub('\]', '', line4)
#docker_name = re.sub('"', '', line5)
#print(docker_name)
print "Service check : ", out
status = ("systemctl status %s")%out
stat = os.system(status)
#stats = os.popen("status").read()
#status = os.system("systemctl status %s | grep Active | awk {'print $1$2'}") %docker_name
#print "Status:", stat

#cmd = ['systemctl', 'status', '%s' %(docker_name), '|', 'grep', 'Active', '|', 'awk', "{'print $1$2'}"]
#proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
#process_output = [j[0] for j in [i.split('\n') for i in proc.stdout.readlines()]]
#process_output = proc.stdout.readlines()[2].split(' ')
#print ' '.join(process_output)
#print "out:", process_output

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
