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
  not(status is null or status=='') -- solo con estado
;
