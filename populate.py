#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DBLite, one_factory
from core.util import chunks

db = DBLite("meneame.db", debug_dir="sql/")
api = Api()

MAX_THREAD=10

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.commit()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()


def my_range(db, api):
    avoid = list(db.select("select id from LINKS", row_factory=one_factory))
    for i in range(api.max_min.id-1, 0, -1):
        if i not in avoid:
            p = api.get_link_info(i)
            if p:
                yield p

def get_links(q, LKS):
    while not q.empty():
        api, user = q.get()
        posts = api.get_list(sent_by=user)
        print("%4d" % len(posts), user)
        if posts:
            LKS.append(posts)
        q.task_done()
    return True

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])


def main():
    db.create_table("LINKS", api.get_list(rows=1))
    db.insert("LINKS", *api.get_links(), insert_or="replace")
    #db.insert("LINKS", *api.search_links(), insert_or="replace")
    db.commit()
    users = list(db.select("select distinct user from LINKS order by user", row_factory=one_factory))
    for usr in chunks(users, MAX_THREAD):
        q = Queue(maxsize=0)
        LKS=[]
        num_theads = len(usr)
        for user in usr:
            q.put((api, user))
        for i in range(num_theads):
            worker = Thread(target=get_links, args=(q, LKS))
            worker.setDaemon(True)
            worker.start()
        q.join()
        for posts in LKS:
            db.insert("LINKS", *posts, insert_or="replace")
        db.commit()
    for i, p in enumerate(my_range(db, api)):
        print(p["id"], "               ", end="\r")
        db.insert("LINKS", **p)
        if i % 1000 == 0:
            db.commit()
    #comments = api.get_comments(*posts)
    #db.full_table("COMMENTS", comments)
    db.commit()


if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
