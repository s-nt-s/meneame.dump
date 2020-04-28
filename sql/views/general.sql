SET @cutdate1 := (SELECT max(sent_date)-604800 FROM LINKS);
SET @cutdate2 := (select UNIX_TIMESTAMP(CAST(DATE_FORMAT(from_unixtime(@cutdate1) ,'%Y-%m-01 00:00:00') as DATETIME)));
SET @cutdate := (select CASE
  when @cutdate1<@cutdate2 then @cutdate1
  else @cutdate2
end
);

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
  tags,
  domain,
  from_unixtime(`date`) main_date,
  from_unixtime(sent_date) sent_date,
  from_unixtime(sent_date+604800) closed_date, -- fecha en que la noticia ya esta cerrada,
  (HOUR(from_unixtime(sent_date))*60)+MINUTE(from_unixtime(sent_date)) minuto, -- minuto del dia en que se envio
  YEAR(from_unixtime(sent_date))+(MONTH(from_unixtime(sent_date))/100) mes, -- mes en el que se envio la noticia
  YEAR(from_unixtime(sent_date))+((
    floor((MONTH(from_unixtime(sent_date))-1)/3)+1
  )/100) trimestre -- trimeste en el que se envio la noticias
from
  LINKS
where
  sub_status_id = 1 and -- solo noticias de la edicion general
  votes != 0 and -- si tiene 0 votos es una noticia erronea
  sent_date < @cutdate -- solo noticias cerradas y de meses ya finalizados
;

UPDATE GENERAL SET domain='20minutos.es' where domain in ('20minutos.com', '20minutos.tv', 'amp.20minutos.es');
UPDATE GENERAL SET domain='bandaancha.eu' where domain = 'bandaancha.st';
UPDATE GENERAL SET domain='elpais.com' where domain = 'elpais.es';
UPDATE GENERAL SET domain='gizmodo.com' where domain = 'gizmodo.es';
UPDATE GENERAL SET domain='lavanguardia.com' where domain = 'lavanguardia.es';
UPDATE GENERAL SET domain='bbc.co.uk' where domain = 'bbc.com';
UPDATE GENERAL SET domain='elmundo.es' where domain = 'el-mundo.es';
UPDATE GENERAL SET domain=REPLACE(domain, '.el-mundo.es', '.elmundo.es') where domain like '%.el-mundo.es';


ALTER TABLE GENERAL
ADD PRIMARY KEY (id),
ADD INDEX ndx_glinks_status (status ASC),
ADD INDEX ndx_glinks_sub (sub ASC);
