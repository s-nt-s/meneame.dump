#!/bin/bash

UA="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0"
l=$(curl -s "https://www.meneame.net" | sed -rn 's/.* href="\?page=([0-9][0-9][0-9][0-9]*).*/\1/p')
		
for p in $(seq 38 $l); do 
	o=$(expr $l - $p)
	d=$(expr $o / 100)
	pt=$(printf "html/portada/%02d" $d)
	out=$(printf "$pt/%04d.html" $o)
	if [ ! -f "$out" ]; then
		mkdir -p "$pt"
		wget -nv --user-agent "$UA" "https://www.meneame.net/?page=$p" -O "$out"
		if grep --quiet -E " id=\"a-shake-[^>]+>men.alo</a>" "$out"; then
			rm "$out"
			continue
		fi
		for s in $(grep -ohE "href=\"/story/[^\"]+" "$out" | cut -d\" -f2 | uniq | tail -n 20 | sort | uniq); do
			str="html$s.html"
			if [ ! -f "$str" ]; then
				wget -nv --user-agent "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0" "https://www.meneame.net$s" -O "$str"
			fi
		done
		sed -e 's/<div /\n<div /g' -i "$out"
		sed -e 's/<\/div>/<\/div>\n/g' -i "$out"
	fi
done

