from core.api import Api
from core.threadme import ThreadMe
import os
import json
from glob import glob
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
os.makedirs("js", exist_ok=True)

api=Api()

tm = ThreadMe(
    max_thread=500,
    list_size=15000
)

fields=set(api.link_fields_info) - set((
    'media_access', 'content', 'content_type', 'encoding', 'html', 'id', 'image', 'thumb_status', 'thumb_url', 'title', 'uri', 'url', 'url_description', 'url_title', 'avatar', 'media_date', 'media_extension', 'media_mime', 'media_size'
))
fields=tuple(sorted(fields))

def get_info(id):
    r = api.get_link_info(id, *fields)
    print(id, end="\r")
    return r

id = api.get_list(status='published', rows=1)
id = int(id[0]["id"])

ini = [int(i.split("-")[-1].split(".")[0]) for i in glob("js/*.json")]
if len(ini)==0:
    ini = 1
else:
    ini = sorted(ini)[-1]

for rows in tm.list_run(get_info, range(ini,id+1)):
    rows = sorted(rows, key=lambda x:x["id"])
    name = "js/%s.json" % (rows[-1]["id"])
    with open(name, "w") as f:
        json.dump(rows, f)
