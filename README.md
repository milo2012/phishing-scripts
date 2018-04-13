# phishing-scripts
Some miscellaneous phishing scripts

| Script | Description |
| --- | --- |
| refLinksToWhite.ps1 | This script is to be used with 'subdoc_injector.py' as mentioned in https://rhinosecuritylabs.com/research/abusing-microsoft-word-features-phishing-subdoc/. The script will change the color of Subdoc reference link to 'white' and saves it<br>Example: .\test.ps1 z:\tmp\test.docx \\1.1.1.1\docs\ |
| o365.py | This script search/download emails/attachments matching keywords from Office365 email accounts|  
| gophishauto.py | This script monitors Gophish campaigns and sends out a Slack/Pushover notification when a set of credentials is captured. It display some statics from the campaign (e.g % of users who read the email/clicked the link/entered credentials as well as who they are).  It also displays the list of credentials captured so far. It also tries to determine the OS used by the users based on the User Agent information [some minor bugs pending to be fixed]|

  

