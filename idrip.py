import requests
import xml.etree.ElementTree as ET
import os
import sys
import time
import cfscrape
from eta import ETA

global PageLimit
global RateLimit
global XMList
XMList = []
RateLimit = 500
PageLimit = 500

def ReadCommandLine():

	global total
	total = []
	total = sys.argv
	total.pop(0)

def MakeURL():

	global ParsedBaseURL

	baseURL = 'https://e621.net/post/index.xml?tags='
	taglen = len(total) - 1

	for each in total:
		pos = total.index(each)
		if pos == 3:
			baseURL = baseURL + each
		else:
			baseURL = baseURL + each + '+'

	ParsedBaseURL = baseURL + '&limit=' + str(PageLimit)
	ParsedBaseURL = ParsedBaseURL + '&page='
	print (str(ParsedBaseURL))
def  APIConnection(PageNum):
	scraper = cfscrape.create_scraper()
	ReqHeader = {'User-Agent': 'e6Scraper'}
	#print (scraper.get(ParsedBaseURL + str(PageNum), headers=ReqHeader).content)
	r = scraper.get(ParsedBaseURL + str(PageNum), headers=ReqHeader)
	#print (str(ParsedBaseURL + str(PageNum)))
	APIXML = r.content
	APIroot = ET.fromstring(APIXML)
	
	Bac = False
	for e in APIroot.findall('post'):
		Bac = True
	if Bac == False:
		#print (str(r))
		return False
	XMList.append(r)
	return True

def Loop(TotalPosts):

	cnt = 0
	Bal = True
	
	PageNum = 0
	MakeURL()
	eta = ETA(TotalPosts / 320)
	file = open (str(total[0])+str(total[1]+'.txt'), 'w+')
	while Bal == True:
		Bal = APIConnection(PageNum + 1)
		time.sleep(RateLimit/1000)
		if not cnt <= TotalPosts:
			Bal = False
		cnt += 320
		eta.print_status()
		PageNum +=1
	eta.done()
	
	
	print ('Parsing XML')
	for each in XMList:
		root = ET.fromstring(each.content)
		for e in root.findall('post'):
			file.write('https://e621.net/post/show/' + e.find('id').text + '\n')		
					
		print ('    '+str(cnt)+'  '+ str(TotalPosts))
			
	file.close()
	eta.done()
	cntttl = cnt / TotalPosts
	cntttl = cntttl * 100
	print ('DL ' + str(cnt) + ' Posts or ' + str(cntttl) + '%' )




if __name__ == '__main__':

	global TotalPosts

	ReadCommandLine()
	
	scraper = cfscrape.create_scraper() # Getting around cloudflare

	MakeURL()
	ReqHeader = {'User-Agent': 'e6Scraper'}
	r = scraper.get(ParsedBaseURL + '0', headers=ReqHeader)
	XML = r.content
	root = ET.fromstring(XML)
	for e in root.getiterator('posts'):
		TotalPosts = int((e.attrib['count']))
	
	print ('Found ' + str(TotalPosts) + ' Posts')


	Loop(TotalPosts)
	
