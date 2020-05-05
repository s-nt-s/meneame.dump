from core.api import Api, tm_search_user_data
from core.threadme import ThreadMe
import os
import json
from .util import mkBunch
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
    info = {
        "users":{
            "max":(db.one("select max(user_id) from (select user_id from LINKS union select user_id from COMMENTS) T") or 0) + 1,
            "max_create": (db.one("select max(id) from USERS where `create` is not null") or 0)+1,
            "live": db.to_list("select id from USERS where live=1 order by id"),
        },
        "comments": {
            "user_id": db.to_list("select id from COMMENTS where user_id is null")
        },
        "links": {
            "user_id": db.to_list("select id from LINKS where user_id is null")
        }
    }
    info["users"]["null_create"]=db.to_list("select id from USERS where id<%s and `create` is null order by id" % info["users"]["max_create"])
    info["posts"] = (db.one("select max(id) from POSTS") or 0)+1
    db.close()
    with open(file_name, "w") as f:
        json.dump(info, f, indent=1)

    sys.exit()

print("-- BEGIN")
info=mkBunch(file_name)

def get_user_id(what, id):
    user_id = api.get_info(what=what, id=id, fields="author")
    if user_id is None:
        return None
    return (id, user_id)

def get_link_user_id(id):
    return get_user_id("link", id)

def get_comment_user_id(id):
    return get_user_id("comment", id)

def get_user_info(id):
    usr = tm_search_user_data(id)
    if usr is None or usr.id is None:
        return None
    dt = usr.meta.get('usuario desde')
    if usr.meta.get('usuario desde') is None or usr.live is None:
        return None
    return usr

tm = ThreadMe(
    max_thread=50,
    list_size=2000
)

print("-- LINKS.user_id")
sql = "update LINKS set user_id={0} where id = {1};"
for id, user_id in tm.run(get_link_user_id, info.links.user_id):
    print(sql.format(user_id, id))

print("-- COMMENT.user_id")
sql = "update COMMENT set user_id={0} where id = {1};"
for id, user_id in tm.run(get_comment_user_id, info.comments.user_id):
    print(sql.format(user_id, id))

sql = """
insert into USERS (id, `create`, `live`) values
({id}, STR_TO_DATE('{create}', '%d-%m-%Y'), {live}) on duplicate key update
`create`=STR_TO_DATE('{create}', '%d-%m-%Y'), `live`={live};
""".strip().replace("\n", " ")

def gnr_users():
    for i in info["users"]["null_create"]:
        yield i
    for i in range(info["users"]["max_create"]+1, info["users"]["max"]+1):
        yield i

print("-- USERS.create")
for usr in tm.run(get_user_info, range(info.user.max_create, info.user.max)):
    live = "0" if usr.live is False else "1"
    i_sql = sql.format(id=usr.id, create=usr.meta['usuario desde'], live=live)
    i_sql.replace(", 1)", ")").replace(", `live`=1;", ";")
    print(i_sql)

def get_user_info(id):
    usr = tm_search_user_data(id)
    if usr and usr.live is False:
        return id
    return None

print("-- USERS.live")
for ids in tm.list_run(get_user_info, info.users.live):
    print("update USERS set live=0 where", gW(ids)+";")


def get_post_info(id):
    return api.get_post_info(id)

print("-- POSTS")
for p in tm.run(get_post_info, range(info["posts"], api.last_post+1)):
    p = {k:(v or "NULL") for k,v in p.items()}
    print("INSERT INTO POSTS (id, `date`, votes, karma, user_id) VALUES ({id}, {date}, {votes}, {karma}, {user_id});".format(**p))

print("-- END")
