# Example: FTP/SFTP connections
import ftplib
import paramiko

# FTP connection
ftp = ftplib.FTP('ftp.example.com')
ftp.login('user', 'pass')

# SFTP connection
ssh = paramiko.SSHClient()
ssh.connect('sftp.example.com', username='user', password='pass')
sftp = ssh.open_sftp()
