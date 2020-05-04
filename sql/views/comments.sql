CREATE OR REPLACE TABLE GENERAL_COMMENTS AS
select
  link,
  id,
  from_unixtime(`date`) main_date,
  votes,
  karma,
  `order`,
  user_id,
  (votes>8 and karma<0) negative, -- segun https://github.com/Meneame/meneame.net/blob/master/www/libs/comment.php#L352
  CAST(YEAR(from_unixtime(`date`))+(MONTH(from_unixtime(`date`))/100) as DECIMAL(6,2)) mes -- mes en el que se envio la noticia
from
  COMMENTS
where link in (select id from GENERAL)
;

ALTER TABLE GENERAL_COMMENTS
ADD PRIMARY KEY (id),
ADD INDEX ndx_gcomments_link (link ASC);
