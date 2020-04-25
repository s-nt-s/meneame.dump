import yaml
from glob import glob
import os
import re
import argparse

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

def parse_tag(tag, main=True):
    tag = re_sp.sub(" ", tag).strip()
    while main and len(tag)>2 and (tag[0]+tag[-1]) in ("''", '""', "``", "´´", "`´", "´`", "[]", "()"):
        tag = tag[1:-1]
    if len(tag)==0 or (main and len(tag)<2):
        return None
    tags = tag.split()
    if len(tags)>1:
        tags=[parse_tag(t, main=False) or t for t in tags]
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
    if tag == "meneame":
        return "Menéame"
    if tag == "españa":
        return "España"
    if tag == "Europa":
        return "Europa"
    return original

def extract_tags(tags):
    tags = tags.lower().strip().split(",")
    tags = set(t.strip() for t in tags if t.strip())
    tags = set([parse_tag(t) for t in tags])
    tags = sorted(t for t in tags if t is not None)
    return tags

def mkArg(title, **kargv):
    parser = argparse.ArgumentParser(description=title)
    for k, h in kargv.items():
        if len(k)==1:
            k = "-" + k
        else:
            k = "--" + k
        parser.add_argument(k, action='store_true', help=h)
    args = parser.parse_args()
    if "silent" in kargv:
        args.trazas = not args.silent
    return args
