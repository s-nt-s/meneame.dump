from core.util import PrintFile
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

username=getpass(prompt='User: ')
password=getpass(prompt='Password: ')
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

def get_files(y=2017):
    while isdir(ROOT+str(y)):
        print("-- "+str(y))
        for fl in glob(ROOT+str(y)+"/*.html.gz"):
            link = fl.split("/")[-1]
            link, page = link.split("-", 1)
            link = int(link)
            page = page.split(".")[0]
            page = int(page)
            if getsize(fl) == 0:
                fl = fl[:-3]
                if not isfile(fl):
                    r = get_response(link, page)
                    if r is None:
                        print("-- size=0 "+fl)
                        continue
                    else:
                        with open(fl, "wb") as f:
                            f.write(r.content)
            yield Bunch(
                year=y,
                link=link,
                page=page,
                file=fl
            )
        y = y + 1

def get_soup(fl):
    f = None
    soup = None
    try:
        if fl.endswith(".gz"):
            f = gzip.open(fl, 'r')
        else:
            f = open(fl, "r", errors='ignore')
        soup = BeautifulSoup(f.read(), "html.parser")
    except UnicodeDecodeError:
        print("-- UnicodeDecodeError "+fl)
    except OSError:
        print("-- OSError "+fl)
    if f is not None:
        f.close()
    return soup

def get_nodes(select=None):
    for fl in get_files():
        if getsize(fl.file) == 0:
            print("-- size=0 "+fl.file)
            continue
        soup = get_soup(fl.file)
        if soup is not None:
            if select is None:
                yield fl.link, soup
            else:
                for node in soup.select(select):
                    yield fl.link, node

def get_items():
    for link, div in get_nodes("div.comment.strike"):
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
insert into STRIKES (link, comment, reason) values
({link}, {comment}, '{reason}');
""".strip()
for s in get_items():
    isql = sql.format(**dict(s))
    isql = re_none.sub(", null);", isql)
    print(isql)
pf.pop()
