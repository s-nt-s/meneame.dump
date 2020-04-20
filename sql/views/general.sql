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
  round((HOUR(from_unixtime(sent_date))*60)+MINUTE(from_unixtime(sent_date)+(SECOND(from_unixtime(sent_date))/60))) minuto, -- minuto del dia
  YEAR(from_unixtime(sent_date+604800))+(WEEKOFYEAR(from_unixtime(sent_date+604800))/100) semana, -- semana en la que se cerro la noticia
  YEAR(from_unixtime(sent_date+604800))+(MONTH(from_unixtime(sent_date+604800))/100) mes -- mes en la que se cerro la noticia
from
  LINKS
where
  sub_status_id = 1 and -- solo noticias de la edicion general
  votes != 0 and -- si tiene 0 votos es una noticia erronea
  sent_date < @cutdate and -- solo noticias cerradas
  (votes>1 or negatives>0) -- si solo esta el voto del autor, la noticia no la 'vio' nadie
;

ALTER TABLE GENERAL
ADD PRIMARY KEY (id),
ADD INDEX ndx_status (status ASC),
ADD INDEX ndx_sub (sub ASC);
