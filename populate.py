#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DBLite, one_factory
from core.threadme import ThreadMe
from core.util import read_yml_all, readlines

db = DBLite("meneame.db", debug_dir="sql/", commit_each=1000)
api = Api()
tm = ThreadMe(
    fix_param=api,
    max_thread=30
)
id_cursor = None
user_ban = set()

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.commit()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()


def my_range(max_id, size=100):
    global id_cursor
    if max_id is not None and max_id>0:
        avoid = list(db.select('''
        select distinct id from (
            select id from LINKS
            union
            select id from broken_id where what='link'
        ) t where id<=%s
        ''' % max_id, row_factory=one_factory))
        for i in range(max_id-1, api.first_link["id"]-1, -1):
            id_cursor = i
            if i not in avoid:
                yield i
                size = size - 1
                if size < 0:
                    break

def get_user_links(api, user):
    if user in user_ban:
        return None
    posts = api.get_list(sent_by=user)
    print("%4d" % len(posts), user)
    if len(posts)==0:
        user_ban.add(user)
    return posts

def get_info(api, id):
    p = api.get_link_info(id)
    if p:
        print("%7d" % p["id"], end="\r")
        return p
    return id

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_by_user(users):
    if isinstance(users, str):
        users = list(db.select(users, row_factory=one_factory))
    for post in tm.run(get_user_links, users):
        db.insert("LINKS", **post, insert_or="replace")


def main():
    global id_cursor
    if "broken_id" not in db.tables:
        db.execute("sql/broken_id.sql")
    db.create_table("LINKS", api.first_link)
    db.insert("LINKS", *api.get_links(), insert_or="replace")
    db.insert("LINKS", *api.search_links(), insert_or="replace")
    get_by_user('''
        select distinct user from LINKS
        where status not in ('discard', 'autodiscard', 'private')
        order by user
    ''')
    max_user = db.one("select max(substr(user, 3, length(user)-4)) from links where user like '--%--'")
    if max_user not in (None, ''):
        for post in tm.run(get_user_links, range(int(max_user), 0, -1)):
            db.insert("LINKS", **post, insert_or="replace")
    id_cursor = api.max_min.id
    new_users = True
    while id_cursor>1:
        if new_users:
            get_by_user('''
                select distinct user from links where
                status not in ('discard', 'autodiscard', 'private') and
                "go" is null and user not in (
                	select user from links where "go" is not null
                )
                order by user
            ''')
        new_users = False
        for post in tm.run(get_info, my_range(id_cursor)):
            if isinstance(post, int):
                db.insert("broken_id", what='link', id=post, insert_or="replace")
            else:
                db.insert("LINKS", **post, insert_or="replace")
                new_users = True
    #comments = api.get_comments(*posts)
    #db.full_table("COMMENTS", comments)
    #db.commit()

if __name__ == "__main__":
    try:
        #users = set(readlines("users.txt")) - set(db.select("select distinct user from links", row_factory=one_factory))
        #users = sorted(i[1:-1] for i in users)
        #print(len(users))
        #get_by_user(users)
        main()
    finally:
        close_out()
