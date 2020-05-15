from core.db import DB
import json
from glob import glob
from core.util import chunks
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def read(glb):
    for fl in sorted(glob(glb)):
        with open(fl) as f:
            for i in json.load(f):
                yield i

db = DB()

for rows in chunks(read("js/l*.json"), 1000):
    db.replace("LINKS", rows)

for rows in chunks(read("js/c*.json"), 1000):
    db.replace("COMMENTS", rows)

db.commit()
db.close()
