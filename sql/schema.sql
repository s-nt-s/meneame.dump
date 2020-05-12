CREATE DATABASE meneame;
GRANT ALL PRIVILEGES ON meneame.* TO 'meneame'@'localhost' IDENTIFIED BY 'meneame';
FLUSH PRIVILEGES;

use meneame;
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;
SET div_precision_increment = 2;

create table LINKS (
  `id` INT,
  `url` VARCHAR(250),
  `sub` VARCHAR(12),
  `status` VARCHAR(11),
  `sub_status_origen` VARCHAR(11),
  `sub_status` VARCHAR(11),
  `sub_status_id` INT,
  `sub_karma` DECIMAL(10,2),
  `user` VARCHAR(32),
  `clicks` INT,
  `votes` INT,
  `negatives` INT,
  `karma` INT,
  `comments` INT,
  `title` VARCHAR(160),
  `tags` VARCHAR(80),
  `sent_date` INT,
  `date` INT,
  `content` VARCHAR(65535),
  `user_id` INT,
  `domain` VARCHAR(253),
  PRIMARY KEY (id)
);

create table COMMENTS (
  `link` INT,
  `id` INT,
  `date` INT,
  `votes` INT,
  `karma` INT,
  `order` INT,
  `user` VARCHAR(32),
--  `content` TEXT,
  `user_id` INT,
  PRIMARY KEY (id)
  -- ,FOREIGN KEY (link) REFERENCES LINKS(id)
);

create table POSTS (
  `id` INT,
  `date` INT,
  `votes` INT,
  `karma` INT,
  `user_id` INT,
  PRIMARY KEY (id)
);

create table TAGS (
  `tag` VARCHAR(80),
  `link` INT
  --,PRIMARY KEY (tag, link)
);

commit;

DROP FUNCTION IF EXISTS mes_mod;

DELIMITER //

CREATE FUNCTION mes_mod(x float, md int) RETURNS DECIMAL(6,2) DETERMINISTIC
BEGIN
 DECLARE y INT;
 DECLARE m INT;
 DECLARE t INT;
 DECLARE r DECIMAL(6,2);
 SET y = FLOOR(x);
 SET m = x*100-(y*100);
 SET t = FLOOR((m-1)/md)+1;
 SET t = (y*100)+t;
 SET r = t/100;
 RETURN r;
END; //

CREATE FUNCTION date_mod(x datetime, md int) RETURNS DECIMAL(6,2) DETERMINISTIC
BEGIN
 DECLARE y INT;
 DECLARE m INT;
 DECLARE t INT;
 DECLARE r DECIMAL(6,2);
 SET y = YEAR(x);
 SET m = MONTH(x);
 SET t = FLOOR((m-1)/md)+1;
 SET t = (y*100)+t;
 SET r = t/100;
 RETURN r;
END; //

DELIMITER ;
