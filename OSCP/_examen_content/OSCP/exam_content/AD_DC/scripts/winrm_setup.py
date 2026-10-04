# Source - https://stackoverflow.com/a/56682909
# Posted by Arnab Majumder, modified by community. See post 'Timeline' for change history
# Retrieved 2026-10-03, License - CC BY-SA 4.0

import winrm

host = 'oscp.exam'
domain = 'oscp.exam'
user = 'r.andrews'
password = 'BusyOfficeWorker890'

session = winrm.Session(host, auth=('{}@{}'.format(user,domain), password), transport='ntlm')

result = session.run_cmd('ipconfig', ['/all']) # To run command in cmd

result = session.run_ps('Get-Acl') # To run Powershell block
