#!/bin/bash

l=$(curl -s "https://www.meneame.net" | sed -rn 's/.* href="\?page=([0-9][0-9][0-9][0-9]*).*/\1/p')




for p in $(seq 46 $l); do 
	o=$(expr $l - $p)
	out=$(printf "html/portada/%04d.html" $o)
	if [ ! -f "$out" ]; then
		wget -nv --user-agent "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0" "https://www.meneame.net/?page=$p" -O "$out"
	fi
done

for s in $(grep -ohE "href=\"/story/[^\"]+" html/portada/*.html | cut -d\" -f2 | sort | uniq); do
	out="html$s.html"
	if [ ! -f "$out" ]; then
		wget -nv --user-agent "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0" "https://www.meneame.net$s" -O "$out"
	fi
done
