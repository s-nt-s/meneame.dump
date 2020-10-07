from core.api import Api, tm_search_user_data
from core.threadme import ThreadMe
import os
import json
from .util import mkBunch, js_write, get_huecos, PrintFile
from core.util import gW, chunks, mkArg
from core.db import DB
from glob import glob
import sys
import shutil
from math import ceil

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

arg = mkArg("Crea un script wget.sh para descargar todas las noticias con comentarios")

db = DB()
pf = PrintFile()
pf.append("wget.sh")
print('''
#!/bin/bash
mkdir -p html
function _url {
    URL=$(curl -w "%{redirect_url}" -o /dev/null -s  "$1")
    if [ -z "$URL" ]; then
        URL="$1"
    fi
}
function _out {
    L="$1"
    P="$2"
    P=$(printf "%02d" $P)
    OUT="html/${L}-${P}.html.gz"
}
function dwn {
    LINK="$1"
    PAGES="$2"
    _out "$LINK" "$PAGES"
    if [ ! -f "$OUT" ]; then
        _url "https://www.meneame.net/story/${LINK}"
        for (( c=1; c<=$PAGES; c++ )); do
            _out "$LINK" "$c"
            echo -ne "${OUT}              \\033[0K\\r"
            wget -q --header="accept-encoding: gzip" -O "${OUT}" "${URL}/standard/${c}"
        done
    fi
}
'''.strip())
for link, comments in db.select('''
    select
    	id, max(comments) comments
    from (
    	select
    		id,
    		comments
    	from LINKS
    	where comments>0
    	union
    	select
    		link id,
    		count(*) comments
    	from COMMENTS
    	group by link
    ) t
    group by
    	id
    order by
    	id
    '''):
    print('dwn {} {}'.format(link, ceil(comments/100)))
print("echo")
pf.pop()
