#!/bin/bash
cd "$(dirname "$0")"
function dump {
  FILE="$1.sql"
  TABLE=$(echo "$1" | sed 's/^[0-9][0-9]*\-//')
  echo "mysqldump $TABLE > $FILE"
  # sed 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g'
  if [ "$TABLE" == "USERS" || "$TABLE" == "STRIKES" ]; then
    mysqldump --skip-comments meneame "$TABLE" | xz -9 > "$FILE.xz"
  else
    mysqldump --no-create-info --skip-comments meneame "$TABLE" | xz -9 > "$FILE.xz"
  fi
  #mysqldump --no-create-info meneame "$TABLE" | 7z a -si "$FILE"
}
dump 01-LINKS
dump 02-COMMENTS
dump 03-POSTS
dump 04-TAGS
dump 05-STRIKES
dump 06-USERS
