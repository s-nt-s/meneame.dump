SET @cutdate1 := (SELECT max(sent_date)-864000 FROM LINKS);
SET @cutdate2 := (select UNIX_TIMESTAMP(CAST(DATE_FORMAT(from_unixtime(@cutdate1) ,'%Y-%m-01 00:00:00') as DATETIME)));
SET @cutdate := (select CASE
  when @cutdate1<@cutdate2 then @cutdate1
  else @cutdate2
end
);

SET div_precision_increment = 2;

CREATE OR REPLACE TABLE ACTIVIDAD AS
select
  mes,
  user_id,
  sum(links) links,
  sum(comments) comments
from (
  select
    date_mod(from_unixtime(sent_date), 1) mes,
    user_id,
    1 links,
    0 comments
  from
    LINKS
  where `sent_date` < @cutdate
  union all
  select
    date_mod(from_unixtime(`date`), 1) mes,
    user_id,
    0 links,
    1 comments
  from
    COMMENTS
  where `date` < @cutdate
) T
group by
  mes, user_id
;
