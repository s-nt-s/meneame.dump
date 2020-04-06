#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import read_yml_all, readlines
import sys
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

db = DB(debug_dir="sql/")
api = Api()
tm = ThreadMe(
    fix_param=api,
    max_thread=30
)

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.fix()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def main():
    links = api.get_links()
    db.replace("LINKS", links)

def cron():
    db.execute('''
        DROP TABLE IF EXISTS AUX_TABLE;
        create table AUX_TABLE (
           RN INT NOT NULL AUTO_INCREMENT,
           ID INT,
           DT INT,
           PRIMARY KEY (RN)
        );
        insert into AUX_TABLE (DT)
        SELECT sent_date FROM LINKS
        where sent_date is not null
        order by sent_date;
    ''')
    db.commit()
    seconds = db.one('''
        select
            min(A.DT-B.DT) seconds
        from
            AUX_TABLE A join AUX_TABLE B on
            A.RN - 1000 = B.RN
    ''')
    db.execute("DROP TABLE AUX_TABLE;")
    db.commit()
    if seconds is not None:
        print(seconds, int(seconds / (60*60)))
        seconds = seconds / 2
        h = int(seconds / (60*60))
        h = min(h, 12)
        print("15 */{0} * * * {1}".format(h, os.path.realpath(__file__)))

if __name__ == "__main__":
    if len(sys.argv)==2 and sys.argv[1]=="cron":
        cron()
        db.close()
        sys.exit()
    try:
        main()
    finally:
        close_out()
