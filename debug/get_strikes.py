from core.api import Api
from core.threadme import ThreadMe
import os
import json
from glob import glob
import sys
from .util import get_items

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
os.makedirs("st", exist_ok=True)

api=Api()

tm = ThreadMe(
    max_thread=100,
    list_size=1000
)

def get_strikes(id, left_comments):
    #print(id, end="\r")
    arr=[]
    for i, r in api.get_comment_strikes(id, left_comments=left_comments):
        arr.append({"id": i, "strike": r, "link":id})
    return arr

def get_ids(ini):
    for i in get_items(reverse=True):
        if i["id"]<ini:
            continue
        if i["comments"]>0:
            yield i["id"], i["comments"]

for i in tm.run(get_strikes, get_ids(1)):
    print(i["id"], i["strike"])
