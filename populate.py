#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DBLite, one_factory
from core.threadme import ThreadMe

db = DBLite("meneame.db", debug_dir="sql/", commit_each=1000)
api = Api()

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.commit()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()


def my_range(db, api):
    if api.max_min.id is not None:
        avoid = list(db.select("select id from LINKS", row_factory=one_factory))
        for i in range(api.max_min.id-1, 0, -1):
            if i not in avoid:
                yield i

def get_links(api, user):
    posts = api.get_list(sent_by=user)
    print("%4d" % len(posts), user)
    return posts

def get_info(api, id):
    p = api.get_link_info(id)
    if p:
        print(p["id"], "               ", end="\r")
    return p


signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])


def main():
    db.create_table("LINKS", api.get_list(rows=1))
    db.insert("LINKS", *api.get_links(), insert_or="replace")
    #db.insert("LINKS", *api.search_links(), insert_or="replace")
    #db.commit()
    users = list(db.select("select distinct user from LINKS order by user", row_factory=one_factory))
    tm = ThreadMe(
        users,
        get_links,
        fix_param=api,
        max_thread=30
    )
    for post in tm.run():
        db.insert("LINKS", **post, insert_or="replace")
    tm = ThreadMe(
        my_range(db, api),
        get_info,
        fix_param=api,
        max_thread=30
    )
    for post in tm.run():
        db.insert("LINKS", **post, insert_or="replace")
    #comments = api.get_comments(*posts)
    #db.full_table("COMMENTS", comments)
    #db.commit()

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
