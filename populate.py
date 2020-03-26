#!/usr/bin/env python3

import signal
import sys

from core.api import Api
from core.db import DBLite, one_factory

db = DBLite("meneame.db")
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
    avoid = list(db.select("select id from LINKS", row_factory=one_factory))
    for i in range(api.max_min.id-1, 0, -1):
        if i not in avoid:
            p = api.get_link_info(i)
            if p:
                yield p


signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])


def main():
    db.full_table("LINKS", api.get_links())
    #db.full_table("LINKS", api.search_links())
    db.commit()
    for user in list(db.select("select distinct user from LINKS order by user", row_factory=one_factory)):
        posts = api.get_list(sent_by=user)
        if posts:
            print("%4d" % len(posts), user)
            db.full_table("LINKS", api.get_links(sent_by=user))
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
