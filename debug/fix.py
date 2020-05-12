from core.api import Api, tm_search_user_data
from core.threadme import ThreadMe
import os
import json
from .util import mkBunch, js_write, get_huecos
from core.util import gW
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


api=Api()
file_name = "fix.json"

if not os.path.isfile(file_name):
    from core.db import DB
    db = DB()

    def huecos(*args, **kargv):
        return tuple(get_huecos(db, *args, **kargv))

    def intersection(*args):
        s = set(args[0])
        for a in args[1:]:
            s = s.intersection(a)
        return tuple(sorted(a))

    def union(*args):
        s = set(args[0])
        for a in args[1:]:
            s = s.union(a)
        return tuple(sorted(a))

    max_user = (db.one('''
        select max(user_id) from (
            select user_id from LINKS union
            select user_id from COMMENTS union
            select user_id from POSTS union
            select id from USERS
        ) T''') or 0) + 1

    miss_comment=db.to_list("""
        select id from LINKS
        where
            comments>0 and (id, comments) not in (select link, count(*) from COMMENTS group by link)
    """)
    info = {
        "users":{
            "insert": huecos("USERS.id", max_id=max_user),
            "update": db.to_list("select id from USERS where live=1 order by id")
        },
        "posts": {
            "insert": huecos("POSTS.id")#, max_id=api.last_post),
        },
        "comments": {
            "insert": miss_comment,
            "user_id": db.to_list("select id from COMMENTS where user_id is null")
        },
        "links": {
            "insert": huecos("LINKS.id"),
            "user_id": db.to_list("select id from LINKS where user_id is null")
        }
    }
    info["comments"]["done"] = db.to_list("select id from COMMENTS where "+gW(miss_comment, f="link"))
    db.close()
    with open(file_name, "w") as f:
        json.dump(info, f, indent=1)

    sys.exit()

print("-- BEGIN")
info=mkBunch(file_name, shuffle=True)

tm = ThreadMe(
    max_thread=50,
    list_size=2000
)

os.makedirs("js", exist_ok=True)
def get_info(id):
    return api.get_link_info(id)

for i, rows in enumerate(tm.list_run(get_info, info.links.insert)):
    js_write("js/l%03d.json" % i, rows)

def get_info(id):
    cs = api.get_comments(id)
    if not cs:
        return None
    r=[]
    for c in cs:
        if c["id"] not in info.comments.done:
            del c["content"]
            r.append(c)
    return r

for i, rows in enumerate(tm.list_run(get_info, info.comments.insert)):
    rows = api.fill_user_id(rows, what='comments')
    js_write("js/c%03d.json" % i, rows)

def get_user_id(what, id):
    user_id = api.get_info(what=what, id=id, fields="author")
    if user_id is None:
        return None
    return (id, user_id)

def get_link_user_id(id):
    return get_user_id("link", id)

def get_comment_user_id(id):
    return get_user_id("comment", id)

print("-- LINKS.user_id")
sql = "update LINKS set user_id={0} where id = {1};"
for id, user_id in tm.run(get_link_user_id, info.links.user_id):
    print(sql.format(user_id, id))

print("-- COMMENT.user_id")
sql = "update COMMENT set user_id={0} where id = {1};"
for id, user_id in tm.run(get_comment_user_id, info.comments.user_id):
    print(sql.format(user_id, id))

def get_user_info(id):
    usr = tm_search_user_data(id)
    if usr is None or usr.id is None:
        return None
    dt = usr.meta.get('usuario desde')
    if usr.meta.get('usuario desde') is None or usr.live is None:
        return None
    return usr

sql = """
insert into USERS (id, `create`, `live`) values
({id}, STR_TO_DATE('{create}', '%d-%m-%Y'), {live});
""".strip().replace("\n", " ")

print("-- USERS.create")
for usr in tm.run(get_user_info, info.users.insert):
    live = "0" if usr.live is False else "1"
    print(sql.format(id=usr.id, create=usr.meta['usuario desde'], live=live))

def get_user_info(id):
    usr = tm_search_user_data(id)
    if usr and usr.live is False:
        return id
    return None

print("-- USERS.update")
for ids in tm.list_run(get_user_info, info.users["update"]):
    print("UPDATE USERS set live=0 where", gW(ids)+";")

def get_post_info(id):
    return api.get_post_info(id)

print("-- POSTS")
for p in tm.run(get_post_info, info.users.insert):
    p = {k:(v or "NULL") for k,v in p.items()}
    print("replace INTO POSTS (id, `date`, votes, karma, user_id) VALUES ({id}, {date}, {votes}, {karma}, {user_id});".format(**p))

print("-- END")
