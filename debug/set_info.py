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
            if d["id"]<=3293660:
                if ok_ids is not None and d["id"] not in ok_ids:
                    continue
                for k in ("karma", "sub_karma"):
                    v = d.get(k)
                    if v is not None and int(v)==v:
                        d[k]=int(v)
                if d.get("sub_karma") == 0:
                    d["sub_karma"] = None
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
    if len(fields)==1:
        return r[fields[0]]
    return r

def gW(ids, f="id"):
    if len(ids)==1:
        return f+" = "+str(ids.pop())
    return f+" in %s" % (tuple(sorted(ids)), )


db=DB()
grp = get_groups("votes", "negatives")
for f, gr in sorted(grp.items()):
    for v, ids in sorted(gr.items()):
        ids = db.to_list("select id from LINKS where {0} and {1}!={2}".format(gW(ids),f, v))
        if len(ids)==0:
            continue
        if len(ids)>1:
            print("--", len(ids))
        print("UPDATE LINKS set {0} = {1} where {2};".format(f, v, gW(ids)))
    print("commit;")
db.close()
