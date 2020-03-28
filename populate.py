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
tm = ThreadMe(
    fix_param=api,
    max_thread=30
)
id_cursor = None

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.commit()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()


def my_range(db, max_id, size=100):
    global id_cursor
    if max_id is not None and max_id>0:
        avoid = list(db.select("select id from LINKS", row_factory=one_factory))
        for i in range(max_id-1, 0, -1):
            id_cursor = i
            if i not in avoid:
                yield i
                size = size - 1
                if size < 0:
                    break

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
    global id_cursor
    db.create_table("LINKS", api.get_list(rows=1))
    db.insert("LINKS", *api.get_links(), insert_or="replace")
    #db.insert("LINKS", *api.search_links(), insert_or="replace")
    users = list(db.select('''
        select distinct user from LINKS
        where status not in ('discard', 'autodiscard', 'private')
        order by user
    ''', row_factory=one_factory))
    for post in tm.run(get_links, users):
        db.insert("LINKS", **post, insert_or="replace")
    id_cursor = api.max_min.id
    #id_cursor = db.one('select min(id)-1 from links where "go" is null')
    new_users = True
    while id_cursor>1:
        if new_users:
            users = list(db.select('''
                select distinct user from links where
                status not in ('discard', 'autodiscard', 'private') and
                "go" is null and user not in (
                	select user from links where "go" is not null
                )
                order by user
            ''', row_factory=one_factory))
            for post in tm.run(get_links, users):
                db.insert("LINKS", **post, insert_or="replace")
        new_users = False
        for post in tm.run(get_info, my_range(db, id_cursor)):
            db.insert("LINKS", **post, insert_or="replace")
            new_users = True
    #comments = api.get_comments(*posts)
    #db.full_table("COMMENTS", comments)
    #db.commit()

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
