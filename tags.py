#!/usr/bin/env python

import yaml

open("meneame.tags.yml", 'w').close()
with open("meneame.yml", 'r') as stream:
    try:
        docs=yaml.load_all(stream)
	for d in docs:
		if d['tags']:
			tags=[t.strip() for t in d['tags'].split(",") if len(t.strip())>0]
			if len(tags)>0:
				o={
					'published': d['published'],
					'tags': tags
				}
				with open('meneame.tags.yml', 'a') as outfile:
					yaml.safe_dump_all([o], outfile) #, default_flow_style=False,allow_unicode=True, default_style=None)
					outfile.write("---\n")
    except yaml.YAMLError as exc:
        print(exc)
