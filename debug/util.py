
from os.path import abspath, dirname, basename
import os
import json
from glob import glob

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
