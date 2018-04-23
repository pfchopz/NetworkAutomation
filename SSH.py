import paramiko
import getpass

#Create/Gather Variables
ssh = paramiko.SSHClient()
host = input('Enter IP: ')
user = input('Username: ')
secret = getpass.getpass(prompt='Password: ')
command = input('Command: ')

#Bypass untrusted cert error, open SSH socket, execute command and return output
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=22, username=user, password=secret)
stdin, stdout, stderr = ssh.exec_command(command)
output = stdout.readlines()
print(''.join(output))