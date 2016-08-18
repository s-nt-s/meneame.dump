# coding=utf-8
from lxml import html
import json
import time
import bs4
import sys
import glob
import yaml
import os.path
import requests
import re

MMP = "https://www.meneame.net/?page="
size=20
seen=list(range(-101,-1))
# <meta name="keywords" content="apollo,astonautas,alexei leonov,espacio,vosjod 2" />
rtag=re.compile("<meta +name=\"keywords\" +content=\"([^\"]+)",re.UNICODE | re.MULTILINE)

def read(f):
	#print "1"
	html = open(f, "r").read()
	#print "2"
	soup = bs4.BeautifulSoup(html,"lxml")
	#print "3"
	return soup
	
def readonline(url):
	response = requests.get(url)
	soup = bs4.BeautifulSoup(response.text,"lxml")
	return soup

def selectone(a,path,index=0):
	return a.select(path)[index]

def get_tags(story):
	sp=None
	if os.path.isfile("html"+story+".html"):
		html = open("html"+story+".html", "r").read()
	else:
		html = requests.get("https://www.meneame.net"+story).text
	m=rtag.search(html)
	if m:
		return m.group(1)
	return None

def get_news(page):
	sp=read(page)
	news=[]
	for a in sp.select("div.news-body"):
		_link=a.find("a")
		_id=int(_link.attrs['id'].split("-")[-1])
		if _id in seen:
			continue
		seen.append(_id)
		del seen[0]
		_h=a.find("h2")
		if not _h:
			_h=a.find("h1")
		_h=_h.find("a")
		_story=_link.attrs["href"]
		dates=[int(d.attrs['data-ts'].strip()) for d in a.select("div.news-submitted span.ts")]
		new={
			'id': _id,
			'title': _h.get_text().strip(), 
			'url': _h.attrs["href"],
			'author': a.select("div.news-submitted a")[0].attrs["href"].split("/")[-1],
			'body': " ".join([t.string.strip() for t in a.find_all(text=True,recursive=False)]).strip(), 
			'sub': a.select("div.news-details span.tool a")[0].get_text().strip(),
			'story': "https://www.meneame.net"+_story,
			'karma': int(a.select("#a-karma-"+str(_id))[0].get_text().strip()),
			'sent': dates[0], 
			'published': dates[1], 
			'votes': {
				'users': int(a.select("#a-usu-"+str(_id))[0].get_text().strip()),
				'anonymous': int(a.select("#a-ano-"+str(_id))[0].get_text().strip()),
				'negative':int(a.select("#a-neg-"+str(_id))[0].get_text().strip())
			}
		}
		counter=sp.select("span.comments-counter span.counter")
		if len(counter)>0:
			new['comments']=int(counter[0].get_text().strip())
		else:
			new['comments']=0
		new['tags']= get_tags(_story)
		news.append(new)
	return news[::-1]

def readpage(page):
	news=get_news(page)
	if len(news)>0:
		with open('meneame.yml', 'a') as outfile:
			yaml.safe_dump_all(news, outfile, default_flow_style=False,allow_unicode=True, default_style=None)
			outfile.write("---\n")
	else:
		print "SKIP"

if __name__ == "__main__":
	dirs=sorted(glob.glob('html/portada/*'))
	if not os.path.isfile("meneame.yml"):
		open("meneame.yml", 'w').close()
		pags=0
	else:
		f = os.popen("grep \"^id: \" meneame.yml | cut -d' ' -f2")
		ids=f.read().splitlines()
		f.close()
		pags=(len(ids)/(size*100))
		seen=seen + [int(i) for i in ids]
		seen=seen[-3000:]

	for dr in dirs:
		if pags>0:
			pags=pags-1
			continue
		print dr

		htmls=sorted(glob.glob(dr+'/*.html'))
		for page in htmls:
			print page
			readpage(page)

