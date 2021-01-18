from core.util import PrintFile
import os
import sys
import gzip
import bs4
from bunch import Bunch
from glob import glob
import re

if len(sys.argv)==1:
    sys.exit("Ha de dar la ruta donde se encuentran los YYYY/ID-PAGE.html.gz")
ROOT = sys.argv[1]
if not os.path.isdir(ROOT):
    sys.exit(ROOT+" no exite")
ROOT = os.path.abspath(ROOT).rstrip("/")+"/"

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

re_none = re.compile(r", '(None)?'\);")
pf = PrintFile()
pf.append("strikes.sql")

def get_items():
    y=2017
    while os.path.isdir(ROOT+str(y)):
        print("-- "+str(y))
        for fl in glob(ROOT+str(y)+"/*.html.gz"):
            link = fl.split("/")[-1]
            link = link.split("-")[0]
            link = int(link)
            with gzip.open(fl,'r') as f:
                soup = bs4.BeautifulSoup(f.read(), "html.parser")
                for div in soup.select("div.comment.strike"):
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
        y = y + 1

sql = """
insert into STRIKES (link, comment, reason) values
({link}, {comment}, '{reason}');
""".strip()
for s in get_items():
    isql = sql.format(**dict(s))
    isql = re_none.sub(", null);", isql)
    print(isql)
pf.pop()
