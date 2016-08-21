# coding=utf-8
from lxml import html
import signal
import json
import time
import bs4
import sys
import glob
import yaml
import os.path
import requests
import re

OUT="meneame.all.yml"
STR="https://www.meneame.net/story/"
EXIT=False

def signal_handler(signal, frame):
	EXIT=True
	print "Se saldra en la proxima iteracion"
signal.signal(signal.SIGINT, signal_handler)

def get_meta(soup,name,value):
	meta=soup.head.find("meta", attrs={name: value})
	if not meta or "content" not in meta.attrs:
		return None
	content=meta.attrs["content"].strip()
	if len(content)==0:
		return None
	return content

def read(id):
	url=STR+id
	response = requests.get(url)
	soup = bs4.BeautifulSoup(response.text,"lxml")
	body=soup.select("div.news-body")
	if not body or len(body)==0:
		print "ERROR: "+url
		return True
	a=body[0]
	cerrado=a.select("#a-va-"+id+" span.closed")
	if len(cerrado)==0:
		print "ABIERTA: "+url
		return False
	div=a.select("div.news-shakeit")
	if len(div)==0:
		print "SIN SHAKE: "+url
		return False
	status=div[0].attrs['class'][-1].split('-')[-1]
	h1=soup.find("h1")
	if not h1:
		print "SIN h1: "+url
		return False
	dates=[int(d.attrs['data-ts'].strip()) for d in a.select("div.news-submitted span.ts")]
	new={
		'id': int(id),
		'title': h1.get_text().strip(), 
		'url': h1.a.attrs["href"],
		'author': a.select("div.news-submitted a")[0].attrs["href"].split("/")[-1],
		'body': " ".join([t.string.strip() for t in a.find_all(text=True,recursive=False)]).strip(), 
		'sub': a.select("div.news-details span.tool a")[0].get_text().strip(),
		'story': get_meta(soup,"property","og:url"),
		'karma': int(a.select("#a-karma-"+id)[0].get_text().strip()),
		'sent': dates[0], 
		'status': status,
		'votes': {
			'users': int(a.select("#a-usu-"+id)[0].get_text().strip()),
			'anonymous': int(a.select("#a-ano-"+id)[0].get_text().strip()),
			'negative':int(a.select("#a-neg-"+id)[0].get_text().strip())
		}
	}
	if status == "published":
		new['comments']=dates[1]
	counter=a.select("span.comments-counter span.counter")
	if len(counter)>0:
		new['comments']=int(counter[0].get_text().strip())
	else:
		new['comments']=0
	tags=[t.get_text().strip() for t in a.select("span.news-tags a") if len(t.get_text().strip())>0]
	if len(tags)>0:
		new['tags']=tags

	with open(OUT, 'a') as outfile:
		yaml.safe_dump_all([new], outfile, default_flow_style=False,allow_unicode=True, default_style=None)
		outfile.write("---\n")

	return True

if __name__ == "__main__":
	last=0
	if not os.path.isfile(OUT):
		open(OUT, 'w').close()
	else:
		f = os.popen("grep \"^id: \" "+OUT+" | tail -n 1 | cut -d' ' -f2")
		ids=f.read().splitlines()
		f.close()
		if len(ids)>0:
			last=int(ids[0])

	while True:
		last=last+1
		if EXIT or not read(str(last)):
			break

