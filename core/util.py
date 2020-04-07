import yaml
from glob import glob
import os
import re

re_sp = re.compile(r"\s+")

def chunks(lst, n):
    arr = []
    for i in lst:
        arr.append(i)
        if len(arr)==n:
            yield arr
            arr = []
    if arr:
        yield arr

def read_yml_all(*fls):
    if len(fls)==1 and "*" in fls[0]:
        fls=sorted(glob(fls[0]))
    for fl in fls:
        if os.path.isfile(fl):
            with open(fl, 'r') as f:
                for i in yaml.load_all(f, Loader=yaml.FullLoader):
                    yield i

def readlines(*fls):
    if len(fls)==1 and "*" in fls[0]:
        fls=sorted(glob(fls[0]))
    for fl in fls:
        if os.path.isfile(fl):
            with open(fl, 'r') as f:
                for i in f.readlines():
                    i = i.strip()
                    if i:
                        yield i

def parsetag(tag, main=True):
    tag = re_sp.sub(" ", tag).strip()
    while main and len(tag)>2 and tag[0]==tag[-1] and tag[0] in ("'", '"', "`", "´"):
        tag = tag[1:-1]
    if len(tag)==0 or (main and len(tag)<2):
        return None
    tags = tag.split()
    if len(tags)>1:
        tags=[parsetag(t, main=False) or t for t in tags]
        tag = " ".join(t for t in tags if t is not None)
        return tag if len(tag) else None
    original = str(tag)
    for a, b in (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u")
    ):
        tag = tag.replace(a, b)
    if tag == "españa":
        return "España"
    if tag == "Europa":
        return "Europa"
    return original
