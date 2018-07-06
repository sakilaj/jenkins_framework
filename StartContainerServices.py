import os
import paramiko
import subprocess
import json
import sys
import time
paramiko.util.log_to_file('/tmp/paramiko.log')

node = sys.argv[1]
with open('config.ini') as fh:
    data = json.load(fh)

containerIP = data['node'][node]['docker_ip']
username = 'autoinstall'
password = 'kodiak'
host = containerIP
port = 22

def property_file():
    cmd_propertyList = ['ls', '-lrt', '/home/autoinstall/temp/']
    tmp1 = subprocess.Popen(cmd_propertyList, stdout=subprocess.PIPE)
    property_file_name = tmp1.stdout.readlines()[-1].split(' ')[-1].split('\n')[0]
    file_name = '/home/autoinstall/temp/%s' %(property_file_name)
    return (file_name,property_file_name)

def SFTP_Client(host,port,username,password,localpath,filepath):
    transport = paramiko.Transport((host,port))
    transport.connect(username = username, password = password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.put(localpath,filepath)

    sftp.close()
    transport.close()
    return True

def SSH_Client(host,username,password,cmd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,username = username,password = password)
    stdin,stdout,stderr = ssh.exec_command('sudo %s'%(cmd))
    out_list = []
    for line in stdout:
        out_list.append(line.strip('\n'))
    ssh.close()
    return out_list

os.system('rm -rf /root/.ssh/known_hosts')
property_file_out = property_file()
localpath = property_file_out[0]
filepath = '/home/autoinstall/%s' % property_file_out[1]
#filepath = '/home/autoinstall/192.168.26.157_20170328080703.properties'
print 'Localpath : ' + localpath, 'Remotepath: ' + filepath
if SFTP_Client(host,port,username,password,localpath,filepath) == True:
    print "Transfer completed"
    print "Starting the Service exection"
else:
    print "Transfer failed hence exiting further process"
    exit()

if node == 'RLS':
    cmd = "perl /DG/activeRelease/Tools/DockerRLSInstall.pl -configure %s" %(filepath)
else:    
    cmd = "perl /DG/activeRelease/Tools/POCContainerConfig.pl %s" %(filepath)

out = SSH_Client(host,username,password,cmd)
print out

fh = open('resultfile', 'a')
fh.write("\n" + time.strftime("%H:%M:%S") + " : %s container service status log" %(node) + "\n\n")

for i in range(0,len(out)-1,1):
    fh.write(out[i]+ "\n")
    print out[i]
fh.close()

if node == "RMQ":
    print "Executing these scripts as well to start the RMQ services"
    #source /DG/activeRelease/Tools/kodiakScripts.conf && /DG/activeRelease/Tools/RMQConfigTrigger.sh NEW
    #source /DG/activeRelease/Tools/kodiakScripts.conf && /DG/activeRelease/Tools/RMQ-scripts/ConfigureRabbitmq.sh APPLY
