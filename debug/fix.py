from core.api import Api, tm_search_user_data
from core.threadme import ThreadMe
from core.db import DB
import os
import json
from .util import mkBunch, gW
import sys

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

file_name = "fix.json"

if not os.path.isfile(file_name):
    db = DB()
    info = {
        "users":{
            "max":db.one("select max(user_id) from (select user_id from LINKS union select user_id from COMMENTS) T"),
            "create_fill": db.to_list("select id from USERS where `create` is not null order by id"),
            "live_fill": db.to_list("select id from USERS where live=0 order by id"),
        },
        "comments": {
            "user_id": db.to_list("select id from COMMENTS where user_id is null")
        },
        "links": {
            "user_id": db.to_list("select id from LINKS where user_id is null")
        }
    }
    db.close()
    with open(file_name, "w") as f:
        json.dump(info, f, indent=1)

    sys.exit()

info=mkBunch(file_name)

api=Api()

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
    if usr.meta.get('usuario desde') is None or usr.live is None:
        return None
    if usr.id not in info.users.create_fill:
        return usr
    if usr.live is False and usr.id not in info.users.live_fill:
        return usr
    return None

tm = ThreadMe(
    max_thread=500,
    list_size=2000
)
sql = "update LINKS set user_id={0} where id = {1};"
for id, user_id in tm.run(get_link_user_id, info.links.user_id):
    print(sql.format(user_id, id))

sql = "update COMMENT set user_id={0} where id = {1};"
for id, user_id in tm.run(get_comment_user_id, info.comments.user_id):
    print(sql.format(user_id, id))

done = set(info.users.create_fill).intersection(info.users.live_fill)
done = tuple(sorted(done))
gnr = (i for i in range(1, info.users.max+1) if i not in done)
sql = """
insert into USERS (id, `create`, `live`) values
({id}, STR_TO_DATE('{create}', '%d-%m-%Y'), {live}) on duplicate key update
`create`=STR_TO_DATE('{create}', '%d-%m-%Y'), `live`={live};
""".strip().replace("\n", " ")

for usr in tm.run(get_user_info, gnr):
    print(sql.format(id=usr.id, create=usr.meta['usuario desde'], live="0" if usr.live is False else "1"))
