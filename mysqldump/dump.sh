#!/bin/bash
set -e

function dump {
  FILE="$1.sql"
  TABLE=$(echo "$1" | sed 's/^[0-9][0-9]*\-//')
  echo "$ mysqldump $TABLE > $FILE"
  # sed 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g'
  if [ "$TABLE" == "USERS" ] || [ "$TABLE" == "STRIKES" ]; then
    mysqldump --skip-comments meneame "$TABLE" | xz -9 > "$FILE.xz"
  else
    mysqldump --no-create-info --skip-comments meneame "$TABLE" | xz -9 > "$FILE.xz"
  fi
  #mysqldump --no-create-info meneame "$TABLE" | 7z a -si "$FILE"
}
DR_SQL="$(dirname "$0")/../sql"

echo "$ cp 00-SCHEMA.sql"
cp "$DR_SQL/schema.sql" 00-SCHEMA.sql

dump 01-LINKS
dump 02-COMMENTS
dump 03-POSTS
dump 04-TAGS
dump 05-USERS
dump 06-STRIKES

echo "$ cp 07-GENERAL.sql"
cp "$DR_SQL/views/general.sql" 07-GENERAL.sql
echo "$ cp 08-ACTIVIDAD.sql"
cp "$DR_SQL/views/actividad.sql" 08-ACTIVIDAD.sql
echo "$ mk README.md"
cat "$DR_SQL/debug/count.sql" | mysql --table meneame > README.md
