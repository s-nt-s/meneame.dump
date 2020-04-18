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

db = DB()

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

def get_row(id, *fields):
    for r in db.select("select " + ", ".join(fields) + " from LINKS where id = "+str(id), cursor=DictCursor):
        return r
    return None

def get_items(ok_ids=None):
    files = {int(basename(i).split(".")[0]):i for i in glob("js/*.json")}
    for _, fl in sorted(files.items()):
        data = load_json(fl)
        data = sorted(data, key=lambda x:x["id"])
        for d in data:
            if d["id"]<=3287083:
                if ok_ids is not None and d["id"] not in ok_ids:
                    continue
                d["user_id"] = d["author"]
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

print("""
ALTER TABLE LINKS ADD COLUMN sub_karma DECIMAL(10,2) NULL DEFAULT 0 AFTER sub_status_origen;
commit;
""".strip())
groups = get_groups("sub_karma")
for v, ids in sorted(groups["sub_karma"].items()):
    if v == 0:
        continue
    if len(ids)==1:
        ids = "= "+str(ids[0])
    else:
        ids = "in %s" % (tuple(ids), )
    print("UPDATE LINKS set sub_karma = %s\nwhere id %s;" % (v, ids))
print("commit;")
sys.exit()

if False:
    ok_ids = db.to_list("select id from LINKS where user_id is null")
    fields=("user_id",)#("sub_status_id", "sub_status", "status", "sub_status_origen")
    groups = get_groups(*fields, ok_ids=ok_ids, removeNull=False)
    for f in fields:
        for v, _ids in sorted(groups[f].items()):
            if isinstance(v, str):
                v = "'%s'" % v
            for ids in chunks(_ids, 100000):
                if len(ids)==1:
                    ids = "= "+str(ids[0])
                else:
                    ids = "in %s" % (tuple(ids), )
                print("UPDATE LINKS set %s = %s\nwhere id %s;" % (f, v, ids))
        print("commit;")
    sys.exit()

ids = tuple([i["id"] for i in get_items() if i["status"] is None])
print("UPDATE LINKS set status=null where id in %s", (ids, ))
print("commit;")
sys.exit()

fields=("status",)
for l in get_info(*fields):
    status = l.get("status")
    if status is None:
        print(l["id"])
    continue
    sub_status_id = l.get("sub_status_id")
    sub_status = l.get("sub_status")
    sub = l.get("sub")
    sub_status_origen = l.get("sub_status_origen")
    if l.get("is_sub") == 1:
        continue
    if (sub_status is not None and status != sub_status) or (sub_status_origen is not None and status!=sub_status_origen):
        print("http://meneame.net/story/"+str(l["id"]))
        if sub:
            print("http://meneame.net/m/"+sub+"/"+str(l["id"]))
        for k in fields:
            if k in l:
                print(k,"=", l[k], end=" | ")
        print("")

db.close()
