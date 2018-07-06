import paramiko
import os

emsIP = '192.168.26.152'
containerIP = '192.168.26.157'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(emsIP, username='root', password='kodiak')
stdin, stdout, stderr = client.exec_command('perl /DG/activeRelease/SetContainerRLFlag.pl %s' %(containerIP))
for line in stdout:
    print line.strip('\n')
client.close()
