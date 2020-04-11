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

db = DB()
api = Api()
tm = ThreadMe(
    max_thread=30,
    list_size=2000
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
    db.meta.min_link_history_id = max(db.meta.min_link_history_id, id)
    return r

def get_user(user):
    r = api.get_list(sent_by=user)
    print("%4d %-20s" % (len(r), user), end="\r")
    return r

def get_sub_status_id(id):
    print("%7d" % id, end="\r")
    s = api.get_info(what='link', id=id, fields="sub_status_id")
    if s is None or (isinstance(s, str) and not s.isdigit()):
        return None
    if isinstance(s, str):
        s = int(s)
    return {"id":id, "sub_status_id": s}

def main():
    if arg.usuarios:
        print("Calculando estadisticas de usuarios")
        db.execute("sql/update_users.sql")
        print("Obtener usuario máximo...", end=" ")
        max_user = db.one("select max(id) from USERS") or -1
        print(max_user)
        for links in tm.list_run(get_user, range(1, max_user+1)):
            links = api.fill_user_id(links)
            db.ignore("LINKS", links)
    print("Obteniendo info de links faltantes")
    done = set({None})
    min_id  = db.meta.get("min_link_history_id", api.first_link["id"])
    for links in tm.list_run(get_info, db.link_gaps(min_id)):
        links = api.fill_user_id(links)
        db.ignore("LINKS", links)
        db.save_meta("min_link_history_id")
        if arg.usuarios:
            continue
        users = set((i.get("user_id") or i["user"]) for i in links)
        users = users.difference(done)
        if users:
            print("\nRevisando usuarios de links faltantes")
            for links in tm.list_run(get_user, users):
                links = api.fill_user_id(links)
                db.ignore("LINKS", links)
            done = done.union(users)
            print("")
    db.save_meta("min_link_history_id")
    print("Actualizando sub_status_id de published")
    gnr = db.select("select id from LINKS where sub_status_id is null")
    for links in tm.list_run(get_sub_status_id, gnr):
        db.update("LINKS", links, skipNull=True)
    db.commit()

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
