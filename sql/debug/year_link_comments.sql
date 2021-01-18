select
  YEAR(from_unixtime(max(sent_date))) year, id, max(comments) comments
from (
  select
    sent_date,
    id,
    comments
  from LINKS
  union
  select
    null sent_date,
    link id,
    count(*) comments
  from COMMENTS
  group by link
) t
group by
  id
order by
  id
INTO OUTFILE '/tmp/year_link_comments.csv'
FIELDS TERMINATED BY ' '
ENCLOSED BY ''
LINES TERMINATED BY '\n';
