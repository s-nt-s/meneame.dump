
from os.path import abspath, dirname, basename
import os
import json
from glob import glob
from bunch import Bunch

def read(fl, split=None, cast=None):
    with open(fl, "r") as f:
        for l in f.readlines():
            l=l.strip()
            if l:
                if split is None:
                    if cast is not None:
                        l=cast(l)
                    yield l
                else:
                    l = l.split()
                    if len(l)==split:
                        if cast is not None:
                            l = tuple(cast(i) for i in l)
                        yield l

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

def get_items(ok_ids=None, reverse=False):
    files = {int(basename(i).split(".")[0]):i for i in glob("js/*.json")}
    for _, fl in sorted(files.items(), reverse=reverse):
        data = load_json(fl)
        data = sorted(data, key=lambda x:x["id"], reverse=reverse)
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



def mkBunchParse(obj):
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = mkBunchParse(v)
        return obj
    if isinstance(obj, dict):
        data = []
        flag = True
        for k in obj.keys():
            if not isinstance(k, str):
                return {k: mkBunchParse(v) for k, v in obj.items()}
        obj = Bunch(**{k: mkBunchParse(v) for k, v in obj.items()})
        return obj
    return obj

def mkBunch(file):
    if not os.path.isfile(file):
        return None
    with open(file, "r") as f:
        data = json.load(f)
    data = mkBunchParse(data)
    return data
