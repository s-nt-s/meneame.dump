# -*- coding: utf-8 -*-

import json
import logging
import logging.config
import re
import sys
import time
from datetime import datetime, date
from functools import lru_cache

import bs4
import requests
import urllib3
from bunch import Bunch
from dateutil.relativedelta import relativedelta

from .endpoint import EndPoint
from .util import chunks
from .threadme import ThreadMe

fisg1 = re.compile(
    r"^.*\bnew_data\s*=\s*\(\s*(.*)\s*\)\s*;\s*$", re.MULTILINE | re.DOTALL)
fisg2 = re.compile(r'([^"a-z])([a-z]+):',
                   re.MULTILINE | re.DOTALL | re.IGNORECASE)
karma = re.compile(r'\s*\b(?:karma|valor):\s*(-?\d+)', re.IGNORECASE)
sp = re.compile(r'\s+', re.MULTILINE | re.DOTALL | re.IGNORECASE)
dt1 = re.compile(r'(\d\d)/(\d\d)-(\d\d):(\d\d):(\d\d)')
dt2 = re.compile(r'(\d\d)-(\d\d)-(\d\d\d\d) (\d\d):(\d\d) UTC')
dt3 = re.compile(r'(\d\d):(\d\d) UTC')
re_user_id = re.compile(r'^--(\d+)--$')

logger = logging.getLogger()

def str_to_epoch(s, date):
    mt = dt3.match(s)
    if mt:
        h = int(mt.group(1))
        m = int(mt.group(2))
        tm = time.struct_time((date.tm_year, date.tm_mon, date.tm_mday,
                               h, m, date.tm_sec, date.tm_wday, date.tm_yday, date.tm_isdst))
        return int(time.mktime(tm))
    if dt2.match(s):
        tm = time.strptime(s, '%d-%m-%Y %H:%M UTC')
        return int(time.mktime(tm))
    mt = dt1.match(s)
    if mt:
        d = int(mt.group(1))
        m = int(mt.group(2))
        y = date.tm_year
        if date.tm_mon > m or (date.tm_mon == m and date.tm_mday > d):
            year = year - 1
        tm = time.strptime(s + "-" + str(y), '%d/%m-%H:%M:%S-%Y')
        return int(time.mktime(tm))
    return None


def get_response(url, params=None, intentos=None):
    try:
        r = requests.get(url, params=params)
    except requests.exceptions.ConnectionError as e:
        if intentos is not None:
            intentos = intentos - 1
            if intentos == 0:
                return None
        time.sleep(60)
        return get_response(url, params=params, intentos=intentos)
    if r.status_code not in (200, 202):
        if intentos is not None:
            intentos = intentos - 1
            if intentos == 0:
                return None
        time.sleep(60)
        return get_response(url, params=params, intentos=intentos)
    if len(r.text) == 0:
        url = r.url.replace("%2C", ",")
        msg = "%d %s\n\t%s" % (r.status_code, url, r.text)
        # logger.error(msg.strip())
        return None
    return r


def get_json(url, params=None, default=None):
    r = get_response(url, params=params)
    if not r:
        return default
    js = r.json()
    return js


def get_soup(url, params=None, select=None, default=None, intentos=None):
    r = get_response(url, params=params, intentos=intentos)
    if not r:
        return default
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    if select:
        return soup.select(select)
    return soup


def get_comments(url, params):
    items = get_soup(url, params=params, select="div.comment", default=[])
    rs = []
    for i in items:
        obj = {
            "id": int(i.attrs["data-id"].split("-")[-1]),
            "who": i.select("a.username")[0].get_text().strip(),
            "date": int(i.select("span.comment-date")[0].attrs["data-ts"]),
            "votes": int(i.select("div.comment-footer a")[0].get_text().strip())
        }
        msg = i.select("div.comment-text")[0]
        for a in msg.find_all("a"):
            if a.attrs["href"].startswith("/") and a.get_text().strip()[0] in ("#", "@"):
                a.unwrap()
            else:
                del a.attrs["rel"]
                del a.attrs["title"]
        msg.attrs.clear()
        msg = str(msg)
        obj["msg"] = msg[5:-6].strip()
        for cl in i.find("img").attrs["class"]:
            if cl.startswith("u:"):
                obj["uid"] = int(cl[2:])
        rs.append(obj)
    return rs


def get_items(url, params, date, total=-1):
    date = time.localtime(date)
    rs = []
    one_page = True
    page_items = -1
    if "p" not in params:
        params["p"] = 1
        one_page = False
    while True:
        items = get_soup(url, params=params, select="div.item a", default=[])
        for a in items:
            obj = {
                "who": a.get_text().strip()
            }
            for f in a.attrs:
                if f not in ("href", "target"):
                    obj[f] = a.attrs[f]
            img = a.find("img")
            if img:
                src = img.attrs["src"]
                uid = src.split("/")[-1].split("-")[0]
                if uid.isdigit():
                    obj["uid"] = int(uid)
            if obj.get("style", None) == "color: #f00":
                del obj["style"]
                obj["type"] = "negative"
            if obj.get("title", "").startswith(obj["who"] + ": "):
                obj["title"] = obj["title"][len(obj["who"]) + 2:]
            m = karma.search(obj.get("title", ""))
            if m:
                obj["karma"] = int(m.group(1))
                obj["title"] = sp.sub(
                    " ", karma.sub(" ", obj["title"])).strip()
            epoch = str_to_epoch(obj.get("title", ""), date)
            if epoch:
                obj["date"] = epoch
                del obj["title"]
            rs.append(obj)
        len_items = len(items)
        if len_items == 0 or one_page:
            return rs
        if page_items == -1:
            page_items = len_items
        elif len_items < page_items:
            return rs
        if len(rs) == total:
            return rs
        params["p"] = params["p"] + 1
    return rs



def tm_search_user_id(user):
    items = get_soup("https://www.meneame.net/backend/get_user_info.php?id="+user, select="img.avatar", default=[])
    if items:
        src = items[0].attrs["src"]
        src = src.rsplit("/")[-1].rsplit(".")[0]
        src = src.split("-")
        if len(src)==3 and src[0].isdigit():
            id = int(src[0])
            return user, id
    return user, None

class Api:
    MAX_ITEMS = 2000
    SUBS = ('mnm', 'actualidad', 'cultura', 'ocio', 'tecnología', 'emnm')
    STATUS = ('published', 'queued', 'all', 'autodiscard', 'discard', 'abuse', 'duplicated', 'metapublished')

    def __init__(self):
        self.sneaker = EndPoint("backend/sneaker2.php")
        self.sneaker_time = None
        self.link_sneaker = EndPoint("backend/link_sneaker.php")
        self.info = EndPoint("backend/info.php")
        self.link_favorites = EndPoint("backend/get_link_favorites.php")
        self.comment_votes = EndPoint("backend/get_c_v.php")
        self.post_votes = EndPoint("backend/get_p_v.php")
        self.link_votes = EndPoint("backend/meneos.php")
        self.story = EndPoint("story.php")
        self.list = EndPoint("api/list.php")
        self.comment_answers = EndPoint("backend/get_comment_answers.php")
        self.post_answers = EndPoint("backend/get_post_answers.php")
        self.list_subs = EndPoint("backend/get_subs.php")
        self.user_id = {}

    def get_subs(self):
        r = get_json(self.list_subs)
        return r

    def extract_user_id(self, user):
        if user is None or isinstance(user, int):
            return user
        m = re_user_id.match(user)
        if m:
            return int(m.group(1))
        return None

    def populate_user_id(self, *users):
        if not users:
            return None
        search = set()
        for user in users:
            if user not in self.user_id:
                id = self.extract_user_id(user)
                if id is None:
                    search.add(user)
                else:
                    self.user_id[user]=id
        if len(search)==0:
            pass
        elif len(search)==1:
            user = search.pop()
            self.user_id[user] = tm_search_user_id(user)[1]
        else:
            tm = ThreadMe(max_thread=50)
            for user, id in tm.run(tm_search_user_id, sorted(search)):
                self.user_id[user]=id
        return self.user_id.get(users[0])

    def fill_user_id(self, arr):
        isDict = isinstance(arr, dict)
        if isDict:
            arr = [arr]
        users = set(i["user"] for i in arr if i["user"] and ("user_id" not in i or i["user_id"] is None))
        self.populate_user_id(*users)
        for i in arr:
            i["user_id"] = self.user_id.get(i["user"])
        return arr[0] if isDict else arr

    def get_list(self, **kargv):
        if kargv is None:
            kargv = {"rows": Api.MAX_ITEMS}
        elif "rows" not in kargv:
            kargv["rows"] = Api.MAX_ITEMS
        js = get_json(self.list, params=kargv)
        if not js:
            return []
        js = js["objects"]
        if not js or not isinstance(js, list):
            return js
        return js

    def get_sneaker(self, **kargv):
        if self.sneaker_time and ("time" not in kargv or kargv["time"] < self.sneaker_time):
            kargv["time"] = self.sneaker_time
        js = get_json(self.sneaker, params=kargv)
        if not js:
            return []
        self.sneaker_time = js["ts"]
        return js["events"]

    def get_info(self, **kargv):
        js = get_json(self.info, params=kargv)
        if js and "fields" in kargv and kargv["fields"] in js:
            return js[kargv["fields"]]
        return js

    def get_story_url(self, id):
        r = requests.get(self.story, params={
                         'id': id}, allow_redirects=False)
        return r.headers['Location']

    def get_story_log(self, url):
        if isinstance(url, int) or (isinstance(url, str) and url.isdigit()):
            url = self.get_story_url(url)
        if not url.endswith("/log"):
            url = url + "/log"
        rs = []
        items = get_soup(url, select="#voters-container > div", default=[])
        for i in items:
            div = i.findAll("div")
            obj = {
                "date": div[0].find("span").attrs["data-ts"],
                # "sub": div[1].get_text().strip(),
                "event": div[2].get_text().strip(),
                "who": div[3].find("a").get_text().strip()
            }
            rs.append(obj)
        return rs

    def get_story_sneaker(self, params, default=None):
        if isinstance(params, int) or (isinstance(params, str) and params.isdigit()):
            params = {
                'items': 9999999999999999999,
                'v': -1,
                'link': params
            }
        r = get_response(self.link_sneaker, params=params)
        if not r:
            return default
        m = fisg1.match(r.text)
        if not m:
            return default
        js = m.group(1)
        js = fisg2.sub(r'\1"\2":', js)
        return json.loads(js)

    def get_story_favorites(self, id, date=None):
        if not date:
            dt = self.get_info(what='link', id=id, fields='date')
            date = int(dt)
        return get_items(self.link_favorites, params={'id': id}, date=date)

    def get_votes(self, what, id, date=None, total=-1):
        if not date:
            js = self.get_info(what=what, id=id, fields='date,votes')
            total = int(js["votes"])
            if total == 0:
                return []
            date = int(js["date"])
        point = self.link_votes
        if what == 'comment':
            point = self.comment_votes
        elif what == 'post':
            point = self.post_votes
        return get_items(point, params={'id': id}, date=date, total=total)

    def get_answers(self, what, id):
        point = self.comment_answers
        if what == 'post':
            point = self.post_answers
        return get_comments(point, params={'id': id})

    def get_links(self, **kargv):
        posts = {}
        # duplicated metapublished
        # https://github.com/Meneame/meneame.net/blob/master/sql/meneame.sql
        # https://github.com/Meneame/meneame.net/blob/master/www/libs/rgdb.php
        for status in Api.STATUS:
            for p in self.get_list(status=status, **kargv):
                posts[p["id"]] = p
        posts = sorted(posts.values(), key=lambda p: p["id"])
        '''
        if "sub" not in kargv:
            for p in posts:
                p["sub_status_id"]=1
        '''
        return posts

    def search_links(self, word):
        posts = {}
        ms1 = relativedelta(months=1)
        _all = self.get_list(
            s='published queued all autodiscard discard abuse duplicated metapublished', q=word, w="links")
        yield sorted(_all, key=lambda p: p["id"])
        if len(_all) >= 50:
            ini = datetime.fromtimestamp(self.start_epoch)
            epoch = min(int(i['sent_date']) for i in _all)
            fin = datetime.fromtimestamp(epoch)
            ini = ini.date()
            fin = fin.date()
            ini = ini.replace(day=1)
            fin = fin.replace(day=2)
            while ini < fin:
                # https://github.com/Meneame/meneame.net/blob/master/www/libs/search.php
                for status in ('published', 'queued', 'all', 'autodiscard discard abuse duplicated metapublished'):
                    yield dict(Bunch(
                        s=status,
                        q=word,
                        w="links",
                        yymm=ini.strftime("%Y%m"),
                    ))
                ini = ini + ms1

    def get_comments(self, id):
        comments = self.get_list(id=id)
        for c in comments:
            c["link"] = id
        return comments

    @property
    @lru_cache(maxsize=None)
    def link_fields_info(self):
        ep = EndPoint("libs/link.php")
        ep.load()
        re_fields = re.compile(r"\bpublic\s+\$([^\s;]+)", re.IGNORECASE)
        fld = set(re_fields.findall(ep.text))
        ep = EndPoint("libs/link.php")
        ep.load()
        re_fields = re.compile(r"\bAS\s+`?([^\s`,]+)")
        fld = fld.union(set(re_fields.findall(ep.text)))
        fld = sorted(fld)
        id = self.get_list(status='published', rows=1)
        if id and len(id)>0:
            id = id[0]["id"]
            link = {}
            for fl in chunks(fld, 10):
                fl = ",".join(fl)
                obj = self.get_info(what='link', id=id, fields=fl)
                link = {**link, **obj}
            fld = sorted(link.keys())
        return tuple(fld)


    @property
    @lru_cache(maxsize=None)
    def link_fields(self, solo_info=False):
        fld = set(self.link_fields_info)
        kys = self.get_list(rows=1)
        kys = set(kys[0].keys())
        eq = kys.intersection(fld)
        for k in ("username", 'author', "sub_name", 'sub_status_id', 'sub_status', 'sub_status_origen', 'sub_karma'):
            if k in fld:
                eq.add(k)
        if "id" in eq:
            eq.remove("id")
        return tuple(sorted(eq))


    @property
    @lru_cache(maxsize=None)
    def mnm_config(self):
        ep = EndPoint("config.php")
        ep.load()
        re_fields = re.compile(r"\$globals\[\s*'([^']+)'\s*\]\s*=\s*'([^']+)'", re.IGNORECASE)
        cfg = {}
        for k, v in re_fields.findall(ep.text):
            cfg[k]=v
        re_fields = re.compile(r"\$globals\[\s*'([^']+)'\s*\]\s*=\s*([^';]+)", re.IGNORECASE)
        for k, v in re_fields.findall(ep.text):
            if v.isdigit():
                v = int(v)
            cfg[k]=v
        return cfg

    @property
    @lru_cache(maxsize=None)
    def start_epoch(self):
        a = int(self.first_link["sent_date"])
        return a

    @property
    @lru_cache(maxsize=None)
    def first_link(self):
        id = 0
        while True:
            id = id + 1
            l = self.get_link_info(id)
            if l:
                return l


    def get_link_info(self, id, *fields, full=False):
        fields = fields or (self.link_fields_info if full else self.link_fields)
        _link = {"id": id}
        for fl in chunks(fields, 10):
            fl = ",".join(fl)
            obj = self.get_info(what='link', id=id, fields=fl)
            if not obj:
                return None
            _link = {**_link, **obj}
        link = {}
        for k, v in _link.items():
            if v == "":
                v = None
            if k == "username":
                k = "user"
            elif k == "sub_name":
                k = "sub"
            elif k == "author":
                k = "user_id"
            if isinstance(v, str):
                if "karma" in k:
                    v = float(v)
                    if int(v)==v:
                        v=int(v)
                elif v.isdigit():
                    v = int(v)
            link[k] = v
        return link
