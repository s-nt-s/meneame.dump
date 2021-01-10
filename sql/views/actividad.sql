SET @sent_date := (SELECT max(sent_date) FROM LINKS);
SET @cutdate := (select UNIX_TIMESTAMP(CAST(DATE_FORMAT(from_unixtime(@sent_date) ,'%Y-%m-01 00:00:00') as DATETIME)));

SET div_precision_increment = 2;

CREATE OR REPLACE TABLE ACTIVIDAD AS
select
  -- from_unixtime(sent_date) sent_date,
  DATE(sent_date) sent_date,
  HOUR(sent_date) sent_hour,
  user_id,
  sum(links) links,
  sum(comments) comments,
  sum(posts) posts
from (
  select
    from_unixtime(sent_date) sent_date,
    user_id,
    1 links,
    0 comments,
    0 posts
  from
    LINKS
  where `sent_date` < @cutdate
  union all
  select
    from_unixtime(`date`) sent_date,
    user_id,
    0 links,
    1 comments,
    0 posts
  from
    COMMENTS
  where `date` < @cutdate
  union all
  select
    from_unixtime(`date`) sent_date,
    user_id,
    0 links,
    0 comments,
    1 posts
  from
    POSTS
  where `date` < @cutdate
) T
group by
  -- sent_date,
  DATE(sent_date),
  HOUR(sent_date),
  user_id
;
