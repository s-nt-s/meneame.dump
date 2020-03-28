DROP VIEW IF EXISTS LK;
DROP VIEW IF EXISTS USER_OUT;

CREATE VIEW LK AS
select
  id,
  url,
  status,
  clicks,
  votes,
  negatives,
  karma,
  title,
  datetime(sent_date, 'unixepoch', 'localtime') "date"
from LINKS order by ID
;

CREATE VIEW USER_OUT AS
select
  user_id,
  datetime(max(sent_date), 'unixepoch', 'localtime') last_sent,
  count(*) links
from
  LINKS
where user like '--%--'
group by
  user_id
;
