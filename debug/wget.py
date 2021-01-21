import os
import json
from core.util import mkArg, readlines, PrintFile
from math import ceil

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

arg = mkArg('''
Crea un script wget.sh para descargar todas las noticias con comentarios
Previamente hay que lanzar sql/debug/year_link_comments.sql
'''.strip())

pf = PrintFile()
pf.append("wget.sh")
print('''
#!/bin/bash
mkdir -p html
YR=""
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
    OUT="html/${YR}/${L}-${P}.html.gz"
}
function dwn {
    LINK="$1"
    PAGES="$2"
    _out "$LINK" "$PAGES"
    _url "https://www.meneame.net/story/${LINK}"
    for (( c=1; c<=$PAGES; c++ )); do
        _out "$LINK" "$c"
        echo -ne "${OUT}              \\033[0K\\r"
        wget -q --header="accept-encoding: gzip" -O "${OUT}" "${URL}/standard/${c}"
    done
}
'''.strip())
lastyear = None
for l in readlines("../sql/debug/year_link_comments.csv"):
    year, link, comments = map(int, l.split())
    if comments == 0:
        continue
    if year != lastyear:
        print("mkdir -p html/"+str(year))
        print('YR="%s"' % year)
        lastyear = year
    pages = ceil(comments/100)
    print('dwn {} {}'.format(link, pages))
print("echo")
pf.pop()
