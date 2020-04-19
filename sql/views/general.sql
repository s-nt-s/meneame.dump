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
  sent_date,
  YEAR(from_unixtime(sent_date+604800))+(WEEKOFYEAR(from_unixtime(sent_date+604800))/100) semana,
  YEAR(from_unixtime(sent_date+604800))+(MONTH(from_unixtime(sent_date+604800))/100) mes,
from
  LINKS
where
  sub_status_id = 1 and
  votes > 1  and -- descartar links que solo 'vio' su propio autor
--  IFNULL(sub_status, status) is not null and
--  IFNULL(sub_status, status) not in ('autodiscard', 'private', 'abuse') and
  sent_date < @cutdate
;

ALTER TABLE GENERAL
ADD PRIMARY KEY (id),
ADD INDEX ndx_status (status ASC),
ADD INDEX ndx_sub (sub ASC);
