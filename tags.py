#!/usr/bin/env python

import yaml

def get_tags(d):
	if d and 'tags' in d and d['tags']:
		tags=[t.strip() for t in d['tags'].split(",") if len(t.strip())>0]
		if len(tags)>0:
			return tags
	return None

open("meneame.tags.yml", 'w').close()
with open("meneame.yml", 'r') as stream:
    try:
        docs=yaml.load_all(stream)
	for d in docs:
		tags=get_tags(d)
		if tags:
			o={
				'published': d['published'],
				'tags': tags
			}
			with open('meneame.tags.yml', 'a') as outfile:
				yaml.safe_dump_all([o], outfile) #, default_flow_style=False,allow_unicode=True, default_style=None)
				outfile.write("---\n")
		else:
			print str(d)
    except yaml.YAMLError as exc:
        print(exc)
