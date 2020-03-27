DROP VIEW IF EXISTS LK;

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
from LINKS order by ID;
