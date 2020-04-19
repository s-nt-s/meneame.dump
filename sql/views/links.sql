SET @cutdate := (SELECT max(sent_date)-604800 FROM LINKS);

UPDATE LINKS set
  `sub` = 'mnm',
  `sub_status` = 'published',
  `sub_status_id` = 1
where id = 1;

DROP TABLE IF EXISTS links;

CREATE TABLE `links` AS
select
  id,
  url,
  sub,
  CASE
    when sub_status is not null then sub_status
    else status
  END status,
  CASE
    when (sub_status='published' or (sub_status is null and status='published')) and sub_karma>0 then sub_karma
    else karma
  END karma,
  user_id,
  clicks,
  votes,
  negatives,
  comments,
  `date`,
  sent_date
from
  LINKS
where
  sub_status_id = 1 and
  sent_date < @cutdate
;
