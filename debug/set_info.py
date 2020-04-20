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
from core.util import chunks

def remove_control_chars(s):
    return "".join(ch for ch in s if category(ch)[0]!="C")

abspath = abspath(__file__)
dname = dirname(abspath)
os.chdir(dname)

def load_json(fl):
    ex = None
    try:
        with open(fl, "r") as f:
            return json.load(f)
    except Exception as e:
        ex=e
    try:
        with open(fl, "r") as f:
            s = remove_control_chars(f.read())
            return json.loads(s)
    except Exception as e:
        pass
    print(fl)
    raise ex from None

def get_items(ok_ids=None):
    files = {int(basename(i).split(".")[0]):i for i in glob("js/*.json")}
    for _, fl in sorted(files.items()):
        data = load_json(fl)
        data = sorted(data, key=lambda x:x["id"])
        for d in data:
            if d["id"]<=3287083:
                if ok_ids is not None and d["id"] not in ok_ids:
                    continue
                for k in ("karma", "sub_karma"):
                    v = d.get(k)
                    if v is not None and int(v)==v:
                        d[k]=int(v)
                yield d

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
    return r

def gW(ids, f="id"):
    if len(ids)==0:
        return f+" = "+str(ids.pop())
    return f+" in %s" % (tuple(sorted(ids)), )

ids = set()
fl=open("jsid.txt", "w")
for i in get_items():
    fl.write(str(i["id"])+"\n")
    if i["status"] is None:
        ids.add(i["id"])
fl.close()
print("UPDATE LINKS set status = NULL where "+gW(ids)+";")
sys.exit()
print("create table TMP_AUX (id INT);")
for ids in chunks(get_items(),10000):
    print("insert into TMP_AUX (id) VALUES\n")
    for id in ids[:-1]:
        print("(%s)," % id)
    print("(%s);" % ids[-1])
