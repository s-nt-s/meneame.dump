#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import mkArg
from datetime import datetime
import os
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

arg = mkArg(
    "Intenta recuperar todo el historico de meneame.net",
    silent="No imprime trazas"
)
if arg.silent:
    print = lambda *args, **kargv: None

safe_date=None
db = DB()
api = Api()
tm = ThreadMe(
    max_thread=30,
    list_size=100
)

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_info(id):
    print("%7d" % id, end="\r")
    r = api.get_link_info(id)
    return r

def main():
    f = datetime.fromtimestamp(api.safe_date)
    print("Obteniendo links de sent_date < {} ({:%Y.%m.%d})".format(api.safe_date, f), end="\r")
    min_id = (db.one("select max(id) from LINKS where sent_date<"+str(api.safe_date)) or 0) + 1
    print("Obteniendo links de sent_date < {} ({:%Y.%m.%d}) and id > {}".format(api.safe_date, f, min_id))
    for links in tm.list_run(get_info, range(min_id, api.last_link['id'])):
        sz = len(links)
        links = [l for l in links if l['sent_date']<api.safe_date]
        if links:
            db.replace("LINKS", links)
        if len(links)<sz:
            break

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
