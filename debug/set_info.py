from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from os.path import abspath, dirname, basename
import os
import json
from glob import glob
import sys
import string
import re
from unicodedata import category
from MySQLdb.cursors import DictCursor
from core.util import chunks, extract_source
from .util import get_items

def gW(ids, f="id"):
    if len(ids)==1:
        return f+" = "+str(ids.pop())
    return f+" in %s" % (tuple(sorted(ids)), )


import sqlite3
fuentes={}
file = "file:meneame.db?mode=ro"
lt = sqlite3.connect(file, detect_types=sqlite3.PARSE_DECLTYPES, uri=True)
for id, url in lt.execute("select id, url from LINKS where url is not null and url!=''"):
    dom = extract_source(url)
    if dom and "'" not in dom and '"' not in dom and "\\" not in dom:
        fuentes[dom] = fuentes.get(dom, []) + [id]
lt.close()
print('''
ALTER TABLE LINKS ADD domain VARCHAR(253);
''')
for fuente, ids in sorted(fuentes.items()):
    print("UPDATE LINKS set domain = '{0}' where {1};".format(fuente, gW(ids)))
sys.exit()

def remove_control_chars(s):
    return "".join(ch for ch in s if category(ch)[0]!="C")

abspath = abspath(__file__)
dname = dirname(abspath)
os.chdir(dname)

def get_info(*fields, ok_ids=None, removeNull=True):
    for d in get_items(ok_ids=ok_ids):
        obj = {}
        for f in fields:
            v = d.get(f)
            if not removeNull or v is not None:
                obj[f]=v
        if removeNull and len(obj.values())==0:
            continue
        if not removeNull or len(obj.values()):
            obj["id"]=d["id"]
            yield obj

def get_groups(*fields, ok_ids=None):
    r = {k:{} for k in fields}
    for i in get_info(*fields, ok_ids=ok_ids):
        for k in fields:
            v = i.get(k)
            if v is not None:
                if v not in r[k]:
                    r[k][v]=[]
                r[k][v].append(i["id"])
    if len(fields)==1:
        return r[fields[0]]
    return r

for i in get_items():
    extract_source(i.get("url"))
