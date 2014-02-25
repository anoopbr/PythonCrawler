
import datetime
import sys
if len(sys.argv)>=2:
    keyword=sys.argv[1]
else:
    keyword="apple"
import string
if len(sys.argv)>=4:
    threadNo=string.atoi(sys.argv[3])
else:
    threadNo=6

import string
if len(sys.argv)>=3:
    num=string.atoi(sys.argv[2])
else:
    num=5

print "keyword="+keyword
print "Threads:"+str(threadNo)
print "Number:"+str(num)

keys = []
if "+" in keyword:
	keys = keyword.split('+')
	
else:
	keys.append(keyword)

print keys

key = keyword.replace("+"," ")

print "[key] ::"+key

import urllib2, urllib
import urlparse
import base64
import socket
import nltk
import re
import math
socket.setdefaulttimeout(6)
print "initialization...please wait!"

import Queue
urlQueue = Queue.Queue()
urlVisited = []
urlDownloaded = []
urlDict = {}
robotUrlDict = {}
import json
crawl = True

import robotexclusionrulesparser
pat = re.compile(r"\.(gif|gpeg|rtf|pdf|doc|gif|jpeg|jpg|mp3|mpeg|gz|tar|zip|rar|mp3|mp4|avi|rmvb|cgi|midi|gzip|basic|x-midi|x-msvideo|x-pn-realaudio|docx|xls|xlsx|wmv)$")
pat1 = re.compile(r'href="([^"]*)"')
pat2 = re.compile(r"^[^/]]")

start_time = datetime.datetime.now()

def checkRobotTxt(url):
    if url in robotUrlDict:
        return robotUrlDict[url]
    else:
		parsed_uri = urlparse.urlparse(url)
		domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
		rob_url=urlparse.urljoin(domain,"robots.txt")
		try:
			rerp.fetch(rob_url)
			robotUrlDict[url]=rerp.is_allowed('*', url)
			return robotUrlDict[url]
		except:
			robotUrlDict[url]=True
		return robotUrlDict[url]

def getBingResult(userinput):
	bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27'+keyword+'%27&$top=20&$format=Json'
	accountKey = 'J5d1j9h3oeuXW/B/es3IPwL1/tSfXFn1bHOl1waw2q0'
	encAccountKey = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + encAccountKey}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	content = response.read()
	s=json.loads(content)
	for i in range(20):
		if not pat.search(s['d']['results'][i]['Url']):
		    if checkRobotTxt(s['d']['results'][i]['Url']):
		    	if urlQueue.qsize() >= 10:
			    	fetch = False
			    	print "fetched 10 results from Bing"
			    	break
		    	urlQueue.put(s['d']['results'][i]['Url'])
		    	urlVisited.append(s['d']['results'][i]['Url'])
	

def getGoogleResults(userinput):
	fetch = True
	fpgcount = 0
	while (fetch):
	    searchAPI = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=8&'
	    userinput = urllib.urlencode ({'q':userinput})
	    search_string=searchAPI+userinput+'&start='
	    fpgcount += 1
	    req = urllib2.Request(search_string+str(8*fpgcount))
	    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36")
	    response=urllib2.urlopen(req).read()
	    s=json.loads(response)
	    for i in s ['responseData']['results']:
	    	if not pat.search(i['url']):
			    if checkRobotTxt(i['url']):
			    	if urlQueue.qsize() >= 10:
				    	fetch = False
				    	print "fetched 10 results from google"
				    	break
			    	urlQueue.put(i['url'])
			    	urlVisited.append(i['url'])




#getGoogleResults(keyword)
getBingResult(keyword)


from bs4 import BeautifulSoup
import robotexclusionrulesparser
import mechanize

noNeedMIME=set()
noNeedMIME.add("application/rtf")
noNeedMIME.add("application/pdf")
noNeedMIME.add("application/doc")
noNeedMIME.add("image/gif")
noNeedMIME.add("image/jpeg")
noNeedMIME.add("audio/basic")
noNeedMIME.add("audio/midi")
noNeedMIME.add("audio/x-midi")
noNeedMIME.add("audio/x-pn-realaudio")
noNeedMIME.add("video/mpeg")
noNeedMIME.add("video/x-msvideo")
noNeedMIME.add("application/x-gzip")
noNeedMIME.add("application/x-tar")
noNeedMIME.add("audio/mpeg")


def valid_mime_type(mymime):
	global mime_whitelist
	for valid_mime in mime_whitelist:
		if valid_mime in mymime:
			return True
	return False

def get_priority(url,content,tokenized):
	priority = 0
	my_regex = r"\b(?=\w)" + re.escape(key) + r"\b(?!\w)" 
	#find all matching patterns
	pat_match = re.findall(my_regex, content.lower())
	occurence = 0
	for i,word in enumerate(tokenized):
		size = len(keys)
		rank = 0
		for j,k in enumerate(keys):
			my_regex1 = r".*" + re.escape(k) + r".*"
			#seacrh for matching keys
			if re.search(my_regex1, word, re.IGNORECASE):
				rank += 1
				#increase rank if successive keys match
				if (tokenized[i-rank] == keys[j-rank]):
					rank += 1
				occurence += 1 * rank
	#priority =  number of search quote matches + (word matches/total words)
	priority = len(pat_match) + (float(occurence)/len(tokenized))
	return priority

def fetchWebPAge(url):
	try:
		req = urllib2.Request(url)
		response = urllib2.urlopen(req,timeout=1)
		content = response.read()
		urlDownloaded.append(url)
		print url
		soup = BeautifulSoup(content)
		raw = nltk.clean_html(content)
		tokenized = nltk.word_tokenize(raw)
		priority = get_priority(url,content,tokenized)

		br = mechanize.Browser()

		br.open(url)

		for link in br.links():
			new_url = urlparse.urljoin(link.base_url,link.url)
			base = urlparse.urlparse(new_url).hostname
			path = urlparse.urlparse(new_url).path
			finalUrl = "http://"+base+path
			if not pat.search(finalUrl):
				if finalUrl not in urlVisited:
					urlQueue.put(finalUrl)
					urlVisited.append(finalUrl)

	except socket.timeout, e:
	    raise MyException("[TIMEOUT ERROR]:: %r" % e)
	'''
	for tag in soup.findAll('a',href=True):
		print "host ::"+urlparse.urlparse(tag['href']).hostname
		print "path ::"+urlparse.urlparse(tag['href']).path
		tag['href'] = urlparse.urljoin(url,tag['href'])
		print "full ::"+tag['href']
		if url in tag['href'] and tag['href'] not in urlVisited:
			urlQueue.put(tag['href'])
			'''


def page_crawler(urlQueue,robotUrlDict,noNeedMIME,urlDict,num,pat,crawl):
	myfile = open("data/urls.txt","w+")
	while (crawl):
		try:
			url = urlQueue.get()
			if not checkRobotTxt(url):
				print "Robot check failed"
				crawl = False
				break
			if len(urlDownloaded)>=num:
				crawl = False
				break

			fetchWebPAge(url)

		except Exception,e:
			str(e)


	myfile.close()

import threading
class crawlerThread(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
        self.func=func
        self.args=args
    def run(self):
        apply(self.func,self.args)

t =[]

for i in range(threadNo):
    t.append(crawlerThread(page_crawler,(urlQueue,robotUrlDict,noNeedMIME,urlDict,num,pat,crawl)))

for i in range(threadNo):
    t[i].start()

for i in t:
	i.join()

end_time = datetime.datetime.now()
print "----------------------"
print "[Search String]:::: "+keyword
print "[Number of pages]:: "+str(num)
print "[Total Threads]:::: "+str(threadNo)
print "[start_time]::::::: "+str(start_time)
print "[end_time]::::::::: "+str(end_time)
total_time = end_time - start_time
print total_time
print "\n[Seconds]:"+str(total_time.seconds)+"\n[MicroSeconds]:"+str(total_time.microseconds)
print "done!"