
https://github.com/kh4sh3i/ElasticSearch-Pentesting

![[Pasted image 20261003154948.png]]

![[Pasted image 20261003154719.png]]

![[Pasted image 20261003154637.png]]

![[Pasted image 20261003154834.png]]

![[Pasted image 20261003154757.png]]

![[Pasted image 20261003152429.png]]

![[Pasted image 20261003155029.png]]


![[Pasted image 20261003155741.png]]


![[Pasted image 20261003155702.png]]


```
──(bitsentry㉿kali)-[~/…/OSCP/exam_content/machine_110/content]
└─$ sudo john ansible_john --wordlist=/usr/share/wordlists/rockyou.txt         
[sudo] password for bitsentry: 
Sorry, try again.
[sudo] password for bitsentry: 
Created directory: /root/.john
Using default input encoding: UTF-8
Loaded 1 password hash (ansible, Ansible Vault [PBKDF2-SHA256 HMAC-256 128/128 ASIMD 4x])
Cost 1 (iteration count) is 10000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
enterprise       (ansible_encripted)     
1g 0:00:00:04 DONE (2026-10-03 15:56) 0.2183g/s 2235p/s 2235c/s 2235C/s 12345b..1asshole
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 

```

![[Pasted image 20261003160052.png]]

this private key needs copy and accuracy format 

![[Pasted image 20261003161233.png]]