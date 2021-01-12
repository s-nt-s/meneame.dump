#!/bin/bash
cd "$(dirname "$0")"
function dump {
  TABLE=$(echo "$1" | sed 's/^[0-9][0-9]*\-//')
  FILE="$1.sql"
  echo "mysqldump $TABLE > $FILE"
  mysqldump --no-create-info --skip-comments meneame "$TABLE" | xz -9 > "$FILE.xz"
  #mysqldump --no-create-info meneame "$TABLE" | 7z a -si "$FILE"
}
dump 01-LINKS
dump 02-COMMENTS
dump 03-POSTS
