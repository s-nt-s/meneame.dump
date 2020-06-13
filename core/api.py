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
from .util import chunks, extract_domain
from .threadme import ThreadMe

fisg1 = re.compile(
    r"^.*\bnew_data\s*=\s*\(\s*(.*)\s*\)\s*;\s*$", re.MULTILINE | re.DOTALL)
fisg2 = re.compile(r'([^"a-z])([a-z]+):',
                   re.MULTILINE | re.DOTALL | re.IGNORECASE)
karma = re.compile(r'\s*\b(?:karma|valor):\s*(-?\d+)', re.IGNORECASE)
re_sp = re.compile(r'\s+', re.MULTILINE | re.DOTALL | re.IGNORECASE)
dt1 = re.compile(r'(\d\d)/(\d\d)-(\d\d):(\d\d):(\d\d)')
dt2 = re.compile(r'(\d\d)-(\d\d)-(\d\d\d\d) (\d\d):(\d\d) UTC')
dt3 = re.compile(r'(\d\d):(\d\d) UTC')
dt_user = re.compile(r"Usuario\s+desde:\s+(\d\d-\d\d-\d\d\d\d)", re.IGNORECASE)
re_user_id = re.compile(r'^--(\d+)--$')

logger = logging.getLogger()

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0',
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
    'Accept': 'text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    "X-Requested-With": "XMLHttpRequest",
}

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
        r = requests.get(url, params=params, headers=default_headers)
    except requests.exceptions.ConnectionError as e:
        if intentos is not None:
            intentos = intentos - 1
            if intentos == 0:
                return None
        time.sleep(60)
        return get_response(url, params=params, intentos=intentos)
    if r.status_code == 404:
        if "página inexistente" in r.text:
            return None
        return r
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
                obj["title"] = re_sp.sub(
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



def tm_search_user_data(user):
    usr = Bunch(
        id=None,
        nick=None,
        create=None,
        live=None,
        meta={}
    )
    if isinstance(user, str):
        usr.nick = user
    else:
        usr.id = user
    soup = get_soup("https://www.meneame.net/backend/get_user_info.php?id="+str(user))
    if soup is None:
        return usr
    if usr.id is None:
        img = soup.select_one("img.avatar")
        if img:
            src = img.attrs["src"]
            src = src.rsplit("/")[-1].rsplit(".")[0]
            src = src.split("-")
            if len(src)==3 and src[0].isdigit():
                id = int(src[0])
                usr.id=id
    for br in soup.findAll("br"):
        br.replaceWith("\n")
    txt = soup.get_text().strip()
    for l in txt.split("\n"):
        l = l.strip()
        if ":" in l:
            l = tuple(i.strip() for i in l.split(":", 1))
            if l[0] and l[1]:
                usr.meta[l[0].lower()]=l[1]
    if usr.meta.get('usuario desde'):
        m = usr.meta['usuario desde']
        usr.create = datetime.strptime(m, "%d-%m-%Y").date()
    if usr.nick is None:
        usr.nick = usr.meta.get("usuario")
    if usr.nick and usr.id:
        usr.live = usr.nick != "--"+str(usr.id)+"--"
    return usr

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
            self.user_id[user] = tm_search_user_data(user).id
        else:
            tm = ThreadMe(max_thread=50)
            for usr in tm.run(tm_search_user_data, sorted(search)):
                self.user_id[usr.nick]=usr.id
        return self.user_id.get(users[0])

    def fill_user_id(self, arr, what=None):
        isDict = isinstance(arr, dict)
        if isDict:
            arr = [arr]
        users = set(i["user"] for i in arr if i["user"] and ("user_id" not in i or i["user_id"] is None))
        self.populate_user_id(*users)
        if what is not None:
            for i in arr:
                if self.user_id.get(i["user"]) is None:
                    self.user_id[i["user"]] = self.get_info(what=what, id=i["id"], fields="author")
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
        lc = r.headers.get('Location')
        if lc is None:
            return "https://www.meneame.net/story/"+str(id)
        return lc

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

    def get_links(self, fill_user_id=False, **kargv):
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
        if fill_user_id:
            self.fill_user_id(posts, what="link")
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

    def get_comments(self, id, fill_user_id=False):
        comments = self.get_list(id=id)
        if len(comments)==2000 and False:
            url = self.get_story_url(id)
            if url and "/story/" in url:
                visto = set(i["id"] for i in comments)
                pag = 20
                while True:
                    pag = pag + 1
                    url + "/"+str(pag)
                    soup = get_soup(url)
                    com = soup.select("ol.comments-list div.comment[data-id]")
                    if len(com)==0:
                        break
                    for c in com:
                        user = c.select_one("a.username").get_text().strip()
                        c = int(c.attrs["data-id"].split("-")[-1])
                        if c not in visto:
                            visto.add(c)
                            c = self.get_comment_info(c)
                            if c:
                                c["user"] = user
                                comments.append(c)
        for c in comments:
            c["link"] = id
        comments = sorted(comments, key=lambda x:x["order"])
        if fill_user_id:
            self.fill_user_id(comments, what="comment")
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
    def last_post(self):
        soup = get_soup("https://www.meneame.net/notame/")
        if soup is None:
            return None
        ids=set()
        for a in soup.select("a[href]"):
            a=a.attrs["href"]
            if "/notame/" in a:
                a=a.split("/notame/", 1)[-1].rstrip("/")
                if a.isdigit():
                    ids.add(int(a))
        if not ids:
            return None
        return max(ids)

    @property
    @lru_cache(maxsize=None)
    def last_link(self):
        for p in self.get_list(status="queued", rows=1):
            return p

    @property
    @lru_cache(maxsize=None)
    def safe_date(self):
        return self.last_link['sent_date'] - self.safe_wait - 86400

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
    def safe_wait(self):
        return max({k:v for k,v in self.mnm_config.items() if "time" in k and isinstance(v, int)}.values())

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
            if len(fl)==1:
                fl.append("id")
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
        if "url" in fields:
            link["domain"] = extract_domain(link.get("url"))
        return link

    def get_comment_info(self, id, *fields):
        # link strike
        fields = fields or ('date', 'votes', 'karma', 'order', 'author') #'content'
        _link = {"id": id}
        for fl in chunks(fields, 10):
            if len(fl)==1:
                fl.append("id")
            fl = ",".join(fl)
            obj = self.get_info(what='comment', id=id, fields=fl)
            if not obj:
                return None
            _link = {**_link, **obj}
        link = {}
        for k, v in _link.items():
            if v == "":
                v = None
            if k == "author":
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

    def get_post_info(self, id, *fields):
        # link strike
        fields = fields or ('date', 'author', 'karma', 'votes') #'content'
        _link = {"id": id}
        for fl in chunks(fields, 10):
            if len(fl)==1:
                fl.append("id")
            fl = ",".join(fl)
            obj = self.get_info(what='post', id=id, fields=fl)
            if not obj:
                return None
            _link = {**_link, **obj}
        link = {}
        for k, v in _link.items():
            if v == "":
                v = None
            if k == "author":
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

    def get_comment_strikes(self, id, left_comments=-1):
        url = self.get_story_url(id)
        if url and "/story/" in url:
            url = url + "/standard/"
            pag = 0
            while left_comments!=0:
                pag = pag + 1
                soup = get_soup(url + str(pag))
                if soup is None:
                    break
                com = soup.select("ol.comments-list div.comment[data-id]")
                if len(com)==0:
                    break
                left_comments = left_comments - len(com)
                for c in com:
                    cls = c.attrs["class"]
                    if isinstance(cls, str):
                        cls = cls.split()
                    if 'strike' in cls:
                        razon = c.select_one("div.comment-text")
                        if razon is not None:
                            razon = razon.get_text().strip()
                            razon = razon.split(":", 1)[-1].strip()
                        c_id = int(c.attrs["data-id"].split("-")[-1])
                        yield c_id, (razon or "--strike--")
                    '''
                    for k in ("comment", "author"):
                        if k in cls:
                            cls.remove(k)
                    if cls:
                        c = int(c.attrs["data-id"].split("-")[-1])
                        print(c, cls)
                    '''
