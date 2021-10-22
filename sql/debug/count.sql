select
   TB TABLA,
   CT FILAS,
   IFNULL(DATE_FORMAT(MN, '%Y-%m-%d'), '') DESDE,
   IFNULL(DATE_FORMAT(MX, '%Y-%m-%d'), '') HASTA
from (
  select "LINKS" TB, count(*) CT, from_unixtime(min(`sent_date`)) MN, from_unixtime(max(`sent_date`)) MX from LINKS
  union
  select "COMMENTS" TB, count(*) CT, from_unixtime(min(`date`)) MN, from_unixtime(max(`date`)) MX from COMMENTS
  union
  select "POSTS" TB, count(*) CT, from_unixtime(min(`date`)) MN, from_unixtime(max(`date`)) MX from POSTS
  union
  select "TAGS" TB, count(*) CT, null MN, null MX from TAGS
  union
  select "USERS" TB, count(*) CT, min(`create`) MN, max(`create`) MX from USERS
  union
  select "STRIKES" TB, count(*) CT, min(`date`) MN, max(`date`) MX from STRIKES
  union
  select "ACTIVIDAD" TB, count(*) CT, min(`sent_date`) MN, max(`sent_date`) MX from ACTIVIDAD
  union
  select "GENERAL" TB, count(*) CT, min(`sent_date`) MN, max(`sent_date`) MX from GENERAL
) T;
