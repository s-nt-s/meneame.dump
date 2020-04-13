from core.api import Api
from core.threadme import ThreadMe
import os
import json
from glob import glob

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
os.makedirs("js", exist_ok=True)

a=Api()

tm = ThreadMe(
    max_thread=500,
    list_size=2000
)

fields=tuple(sorted(set(a.link_fields_info) - set(('content', 'content_type', 'encoding', 'html', 'id', 'image', 'thumb_status', 'thumb_url', 'title', 'uri', 'url', 'url_description', 'url_title', 'avatar', 'media_date', 'media_extension', 'media_mime', 'media_size'))))

def get_info(id):
    r = api.get_link_info(id, *fields)
    return r

id = self.get_list(status='published', rows=1)
id = int(id[0]["id"])
info = api.get_link_info(id)
keys = []

ini = glob("js/*.json")
if len(ini)==0:
    ini = 1
else:
    ini = sorted(ini)[-1]
    ini = ini.split("-")[-1]
    ini = ini.split(".")[0]
    ini = int(ini)

for rows in tm.list_run(get_info, range(ini,id+1)):
    rows = sorted(rows, key=lambda x:x["id"])
    name = "js/%s-%s.json" % (rows[0], rows[-1])
    with open(name, "w") as f:
        json.dump(rows, f)
