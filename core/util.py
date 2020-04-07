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

def parse_tag(_tag):
    _tag = re_sp.sub(" ", _tag).strip()
    if not _tag:
        return None
    tags = _tag.split()
    if len(tags)>1:
        tags=[parse_tag(t) or t for t in tags]
        return " ".join(tags)
    tag = _tag
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
    return _tag
