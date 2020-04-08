#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import read_yml_all, readlines, mkArg
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

arg = mkArg(
    "Intenta recuperar todo el historico de meneame.net",
    usuarios="Recuperar historico de usuarios",
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
    if arg.usuarios:
        print("Calculando estadisticas de usuarios")
        db.execute("sql/update_users.sql")
        print("Obtener usuario máximo...", end=" ")
        max_user = db.one("select max(id) from USERS") or -1
        print(max_user)
        for links in tm.list_run(get_user, range(1, max_user+1)):
            links = api.fill_user_id(links)
            db.replace("LINKS", links)
            #users = (u["user_id"] for u in links if u["user_id"] and u["user"] == ("--%s--" % u["user_id"]))
    print("Obteniendo info de links faltantes")
    done = set()
    tm.rt_null=[]
    min_id  = db.meta.get("min_link_history_id", api.first_link["id"])
    for links in tm.list_run(get_info, db.link_gaps(min_id)):
        links = api.fill_user_id(links)
        db.ignore("LINKS", links)
        db.meta.min_link_history_id = max([i["id"] for i in links] + tm.rt_null)
        db.save_meta("min_link_history_id")
        if arg.usuarios:
            continue
        users = set(i.get("user_id", i["user"]) for i in links)
        users = users.difference(done)
        if users:
            print("Revisando usuarios de links faltantes")
            for links in tm.list_run(get_user, users):
                links = api.fill_user_id(links)
                db.replace("LINKS", links)
            done = done.union(users)

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
