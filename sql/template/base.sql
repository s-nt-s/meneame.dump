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
from LINKS
where
  sub_status_id = 1 and
  sent_date < {0}
;
