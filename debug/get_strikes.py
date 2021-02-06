from core.util import PrintFile, readlines, read
from os.path import isdir, isfile, abspath, dirname, getsize
from os import chdir
import sys
import gzip
from bs4 import BeautifulSoup
from bunch import Bunch
from glob import glob
import re
from core.web import Web
from getpass import getpass
import time
from math import ceil

if len(sys.argv)==1:
    sys.exit("Ha de dar la ruta donde se encuentran los YYYY/ID-PAGE.html.gz")
ROOT = sys.argv[1]
if not isdir(ROOT):
    sys.exit(ROOT+" no exite")
ROOT = abspath(ROOT).rstrip("/")+"/"

abspath = abspath(__file__)
dname = dirname(abspath)
chdir(dname)

re_none = re.compile(r", '(None)?'\);")

with open("../key", "r") as f:
    username, password = f.read().strip().split()

WB = None
pf = PrintFile()
pf.append("strikes.sql")

def get_response(link, page, intento=1):
    if intento > 3:
        return None
    global WB
    if WB is None:
        WB=Web()
        WB.get("https://www.meneame.net/login")
        r = WB.submit("#login-form", username=username, password=password, silent_in_fail=True)
        if r is None:
            time.sleep(10)
            WB=None
            return get_response(link, page, intento=intento+1)
    WB.get("https://www.meneame.net/story/"+str(link))
    if WB.response.status_code == 200:
        url = WB.response.url+"/standard/"+str(page)
        WB.get(url)
    if WB.response.status_code == 200:
        return WB.response
    WB=None
    return get_response(link, page, intento=intento+1)

def get_soup(fl):
    r = Bunch(
        fl=fl,
        soup=None,
        error=None,
        trace=None
    )
    f = None
    try:
        if fl.endswith(".gz"):
            f = gzip.open(fl, 'r')
        else:
            f = open(fl, "r", errors='ignore')
        r.soup = BeautifulSoup(f.read(), "html.parser")
    except UnicodeDecodeError as e:
        r.error="UnicodeDecodeError"
        r.trace = e
    except OSError as e:
        r.error="OSError"
        r.trace = e
    if f is not None:
        f.close()
    if r.soup and len(r.soup.select("div.comment"))==0:
        r.error="comments=0"
    return r

def get_file(year, link, page):
    fl = ROOT + "{year}/{link}-{page:02d}.html".format(year=year, link=link, page=page)
    r = None
    if isfile(fl):
        r = get_soup(fl)
    else:
        r = get_soup(fl+".gz")
    if r.error and r.fl.endswith(".gz"):
        rsp = get_response(link, page)
        if rsp is None:
            print("-- size=0 "+fl)
            return None
        with open(fl, "wb") as f:
            f.write(rsp.content)
        r = get_soup(fl)
    if r.error:
        print("--", r.error)
        return None
    r.link = link
    r.page = page
    return r


def get_files():
    last_year = None
    for l in readlines("../sql/debug/2017.csv"):
        year, link, comments = map(int, l.split())
        if year<2017 or comments<1:
            continue
        if last_year is None or year!=last_year:
            print("--", year)
            last_year = year
        pages = ceil(comments/100)
        for p in range(1, pages+1):
            r = get_file(year, link, p)
            if r is not None:
                yield r

def get_items():
    for fl in get_files():
        link = fl.link
        for div in fl.soup.select("div.comment.strike"):
            comment = div.select_one("a.comment-expand")
            comment = comment.attrs["data-id"]
            comment = int(comment)
            reason = div.select_one("div.comment-text a")
            if reason:
                reason = reason.get_text().strip()
                reason = reason.split(":", 1)
                reason = reason[-1].strip()
            yield Bunch(
                link=link,
                comment=comment,
                reason=reason
            )

sql = """
insert ignore into STRIKES (link, comment, reason) values
({link}, {comment}, '{reason}');
""".strip()
for s in get_items():
    isql = sql.format(**dict(s))
    isql = re_none.sub(", null);", isql)
    print(isql)
print(read("../sql/strikes/update.sql"))
pf.pop()
