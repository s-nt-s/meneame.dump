SET @cutdate1 := (SELECT max(sent_date)-604800 FROM LINKS);
SET @cutdate2 := (select UNIX_TIMESTAMP(CAST(DATE_FORMAT(from_unixtime(@cutdate1) ,'%Y-%m-01 00:00:00') as DATETIME)));

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
  round((HOUR(from_unixtime(sent_date))*60)+MINUTE(from_unixtime(sent_date)+(SECOND(from_unixtime(sent_date))/60))) minuto, -- minuto del dia en que se envio
  YEAR(from_unixtime(sent_date+604800))+(WEEKOFYEAR(from_unixtime(sent_date+604800))/100) semana, -- semana en la que se cerro la noticia
  YEAR(from_unixtime(sent_date+604800))+(MONTH(from_unixtime(sent_date+604800))/100) mes, -- mes en el que se cerro la noticia
  YEAR(from_unixtime(sent_date))+(MONTH(from_unixtime(sent_date))/100) sent_mes -- mes en el que se envio la noticia
from
  LINKS
where
  sub_status_id = 1 and -- solo noticias de la edicion general
  votes != 0 and -- si tiene 0 votos es una noticia erronea
  sent_date < @cutdate1 and -- solo noticias cerradas
  sent_date < @cutdate2 -- solo quiero analizar meses completos
;

ALTER TABLE GENERAL
ADD PRIMARY KEY (id),
ADD INDEX ndx_status (status ASC),
ADD INDEX ndx_sub (sub ASC);
