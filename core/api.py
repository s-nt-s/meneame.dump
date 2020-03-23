# -*- coding: utf-8 -*-

import json
import logging
import logging.config
import re
import time

import bs4
import requests
import urllib3
import sys
from functools import lru_cache

from .endpoint import EndPoint

fisg1 = re.compile(
    r"^.*\bnew_data\s*=\s*\(\s*(.*)\s*\)\s*;\s*$", re.MULTILINE | re.DOTALL)
fisg2 = re.compile(r'([^"a-z])([a-z]+):',
                   re.MULTILINE | re.DOTALL | re.IGNORECASE)
karma = re.compile(r'\s*\b(?:karma|valor):\s*(-?\d+)', re.IGNORECASE)
sp = re.compile(r'\s+', re.MULTILINE | re.DOTALL | re.IGNORECASE)
dt1 = re.compile(r'(\d\d)/(\d\d)-(\d\d):(\d\d):(\d\d)')
dt2 = re.compile(r'(\d\d)-(\d\d)-(\d\d\d\d) (\d\d):(\d\d) UTC')
dt3 = re.compile(r'(\d\d):(\d\d) UTC')

logger = logging.getLogger()

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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


def get_response(url, params=None):
    r = requests.get(url, params=params)
    if r.status_code not in (200, 202) or len(r.text) == 0:
        url = r.url.replace("%2C", ",")
        msg = "%d %s\n\t%s" % (r.status_code, url, r.text)
        logger.error(msg.strip())
        return None
    return r


def get_json(url, params=None, default=None):
    r = get_response(url, params=params)
    if not r:
        return default
    js = r.json()
    return js


def get_soup(url, params=None, select=None, default=None):
    r = get_response(url, params=params)
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


class Api:
    MAX_ITEMS = 2000

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
        self._max_min_id = None

    def get_list(self, params=None):
        if params is None:
            params = {"rows": Api.MAX_ITEMS}
        elif "rows" not in params:
            params["rows"] = Api.MAX_ITEMS
        js = get_json(self.list, params=params)
        if not js:
            return []
        return js["objects"]

    def get_sneaker(self, params={}):
        if self.sneaker_time and ("time" not in params or params["time"] < self.sneaker_time):
            params["time"] = self.sneaker_time
        js = get_json(self.sneaker, params=params)
        if not js:
            return []
        self.sneaker_time = js["ts"]
        return js["events"]

    def get_info(self, params):
        js = get_json(self.info, params=params)
        if js and params["fields"] in js:
            return js[params["fields"]]
        return js

    def get_safe_info(self, params):
        try:
            return self.get_info(params)
        except requests.exceptions.ConnectionError as e:
            time.sleep(60)
            return sefl.get_safe_info(params)

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
            dt = self.get_info({'what': 'link', 'id': id, 'fields': 'date'})
            date = int(dt)
        return get_items(self.link_favorites, params={'id': id}, date=date)

    def get_votes(self, what, id, date=None, total=-1):
        if not date:
            js = self.get_info(
                {'what': what, 'id': id, 'fields': 'date,votes'})
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

    def get_links(self):
        posts = {}
        max_min_id=-1
        # duplicated metapublished
        # https://github.com/Meneame/meneame.net/blob/master/sql/meneame.sql
        # https://github.com/Meneame/meneame.net/blob/master/www/libs/rgdb.php
        for status in ('published', 'queued', 'all', 'autodiscard', 'discard', 'abuse', 'duplicated', 'metapublished'):
            min_id=sys.maxsize
            for p in self.get_list(params={"status": status}):
                posts[p["id"]] = p
                min_id = min(min_id, p["id"])
            if min_id<sys.maxsize:
                max_min_id = max(max_min_id, min_id)
        self._max_min_id=max_min_id
        posts = sorted(posts.values(), key=lambda p: p["id"])
        return posts

    def get_comments(self, *ids):
        if len(ids) == 0:
            ids = [id for id in self.get_posts()]
        if ids and isinstance(ids[0], dict):
            ids = [i["id"] for i in ids if i["comments"]>0]
        ids = sorted(set(ids))
        comments = {}
        for id in ids:
            for c in self.get_list(params={"id": id}):
                c["post_id"]=id
                comments[c["id"]] = c
        comments = sorted(comments.values(), key=lambda c: c["id"])
        return comments

    @property
    @lru_cache(maxsize=None)
    def link_fields(self):
        ep = EndPoint("libs/link.php")
        ep.load()
        re_fields=re.compile(r"\bpublic\s+\$([^\s;]+)", re.IGNORECASE)
        return re_fields.findall(ep.text)

    def get_link_info(self, id):
        kys = set(self.get_list({"rows":1})[0].keys())
        fld = set(self.link_fields)
        eq = kys.intersection(fld)
        for k in ("username", "sub_name"):
            if k in fld:
                eq.add(k)
        if "id" in eq:
            eq.remove("id")
        eq = sorted(eq)
        _link = {"id": id}
        for fl in chunks(eq, 10):
            fl = ",".join(fl)
            obj = self.get_safe_info({'what': 'link', 'id': id, 'fields': fl})
            if not obj:
                return None
            _link = {**_link, **obj}
        link = {}
        for k, v in _link.items():
            if v in (None, ""):
                continue
            if k == "username":
                k = "user"
            elif k == "sub_name":
                k = "sub"
            link[k]=v
        return link
