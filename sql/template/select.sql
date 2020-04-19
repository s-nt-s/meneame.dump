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
  sent_date < {1}
;



DROP TABLE IF EXISTS LINKS_OK;

create table LINKS_OK (
  `id` INT,
  PRIMARY KEY (id)
);

insert into LINKS_OK (id)
select id
from LINKS
where
  sub in {0} -- solo subs principales
  and
  sent_date < {1} -- solo enlaces cerrados
  and
  not(status is null or status=='' or status='') -- solo con estado
;

select id, sub, CASE
  when sub_status_id == 1 and sub_status is not null then sub_status
  when
