SET @cutdate := (SELECT max(sent_date)-604800 FROM LINKS);

UPDATE LINKS set
  `sub` = 'mnm',
  `sub_status` = 'published',
  `sub_status_id` = 1
where id = 1;

CREATE OR REPLACE TABLE GENERAL AS
select
  id,
  url,
  sub,
  IFNULL(sub_status, status) status,
  CASE
    when sub_karma>0 and IFNULL(sub_status, status)='published' then sub_karma
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
--  IFNULL(sub_status, status) is not null and
--  IFNULL(sub_status, status) not in ('autodiscard', 'private', 'abuse') and
  sent_date < @cutdate
;
