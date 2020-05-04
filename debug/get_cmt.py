from core.api import Api
from core.threadme import ThreadMe
import os
import json
from glob import glob
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

api=Api()

tm = ThreadMe(
    max_thread=500,
    list_size=15000
)

def get_info(id):
    user_id = api.get_info(what="comment", id=id, fields="author")
    if user_id is None:
        return None
    return (id, user_id)

def get_ids():
    with open("cids.txt", "r") as f:
        for l in f.readlines():
            l = l.strip()
            if l:
                yield int(l)

for id, user_id in tm.run(get_info, get_ids()):
    print(id, user_id)
