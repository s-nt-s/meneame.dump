SET @cutdate_aux := (SELECT max(sent_date) FROM LINKS);
SET @cutdate := (select UNIX_TIMESTAMP(CAST(DATE_FORMAT(from_unixtime(@cutdate_aux) ,'%Y-%m-01 00:00:00') as DATETIME)));

SET div_precision_increment = 2;

CREATE OR REPLACE TABLE ACTIVIDAD AS
select
  mes,
  user_id,
  sum(links) links,
  sum(comments) comments,
  sum(posts) posts
from (
  select
    date_mod(from_unixtime(sent_date), 1) mes,
    user_id,
    1 links,
    0 comments,
    0 posts
  from
    LINKS
  where `sent_date` < @cutdate
  union all
  select
    date_mod(from_unixtime(`date`), 1) mes,
    user_id,
    0 links,
    1 comments,
    0 posts
  from
    COMMENTS
  where `date` < @cutdate
  union all
  select
    date_mod(from_unixtime(`date`), 1) mes,
    user_id,
    0 links,
    0 comments,
    1 posts
  from
    POSTS
  where `date` < @cutdate
) T
group by
  mes, user_id
;
