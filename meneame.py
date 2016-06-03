# coding=utf-8
from lxml import html
import json
import time
import bs4
import sys
import glob
import yaml

MMP = "https://www.meneame.net/?page="
seen=list(range(-101,-1))

def read(f):
	html = open(f).read()
	soup = bs4.BeautifulSoup(html,"lxml")
	return soup

def selectone(a,path,index=0):
	return a.select(path)[index]

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
			'tags': [a.select("div.news-details span.tool a")[0].get_text().strip()],
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
		tgs=read("html"+_story+".html").select("span.news-tags a")
		new['tags']= new['tags'] + [t.get_text().strip() for t in tgs]
		news.append(new)
	return news

def write(s,modo,en=3):
	if en in (1,3):
		with open("meneame.json", modo) as f:
			f.write(s+"\n")
	if en in (2,3):
		with open("meneame.mini.json", modo) as f:
			f.write(s+"\n")

def jsn(news):
	js=json.dumps(news)[1:-1].strip()
	return js.replace("}, {","}, \n{")

def readpage(page,first=False):
	news=get_news(page)
	if len(news)>0:
		with open('meneame.yml', 'a') as outfile:
			yaml.safe_dump_all(news, outfile, default_flow_style=False,allow_unicode=True, default_style=None)
			outfile.write("---")
		if not first:
			write(",","a")
		write(jsn(news),"a",1)
		news=[{'date':n['published'],'tags':n['tags']} for n in news]
		write(jsn(news),"a",2)

if __name__ == "__main__":
	htmls=glob.glob('html/portada/*.html')
	open("meneame.yml", 'w').close()
	write("[","w")
	readpage(htmls.pop(0), True)
	for page in htmls:
		readpage(page)
	write("]","a")
        
