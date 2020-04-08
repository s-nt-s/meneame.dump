#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import read_yml_all, readlines
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

arg = mkArg(
    "Intenta recuperar todo el historico de meneame.net",
    silent="No imprime trazas"
)
if arg.silent:
    print = lambda *args, **kargv: None

db = DB(debug_dir="sql/")
api = Api()
tm = ThreadMe(
    fix_param=api,
    max_thread=30,
    list_size=10
)

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.fix()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_info(a, id):
    print("%7d" % id, end="\r")
    r = a.get_link_info(id)
    return r

def get_user(a, user):
    r = a.get_list(sent_by=user)
    print("%4d %s" % (len(r), user), end="\r")
    return r


def main():
    print("Obtener usuario máximo...", end=" ")
    max_user = db.one('''
        select max(id) from (
            select id from USERS
            union
            select user_id id from LINKS
            union
            select user_id id from COMMENTS
        )
    ''') or -1
    print(max_user)
    for links in tm.list_run(get_user, range(1, max_user+1)):
        links = api.fill_user_id(links)
        db.replace("LINKS", links)
    print("Obteniendo info de links faltantes")
    tm.rt_null=[]
    for links in tm.list_run(get_info, db.link_gaps()):
        links = api.fill_user_id(links)
        db.ignore("LINKS", links)
        if tm.rt_null:
            db.replace("broken_id", [{"what": 'link', 'id': i} for i in tm.rt_null])
            tm.rt_null = []
    tm.rt_null=[]

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
