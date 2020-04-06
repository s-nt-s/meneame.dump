CREATE DATABASE meneame;
GRANT ALL PRIVILEGES ON meneame.* TO 'meneame'@'localhost' IDENTIFIED BY 'meneame';
FLUSH PRIVILEGES;

use meneame;
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

create table LINKS (
  `id` INT,
  `url` TEXT,
  `sub` TEXT,
  `status` TEXT,
  `user` TEXT,
  `clicks` INT,
  `votes` INT,
  `negatives` INT,
  `karma` INT,
  `comments` INT,
  `title` TEXT,
  `tags` TEXT,
  `sent_date` INT,
  `date` INT,
  `content` TEXT,
  `user_id` INT,
  PRIMARY KEY (id)
);

create table COMMENTS (
  `link` INT,
  `id` INT,
  `date` INT,
  `votes` INT,
  `karma` INT,
  `order` INT,
  `user` TEXT,
  `content` TEXT,
  `user_id` INT,
  PRIMARY KEY (id),
  FOREIGN KEY (link) REFERENCES LINKS(id)
);

create table COMMENTS (
  `link` INT,
  `id` INT,
  `date` INT,
  `votes` INT,
  `karma` INT,
  `order` INT,
  `user` TEXT,
  `content` TEXT,
  `user_id` INT,
  PRIMARY KEY (id)
  -- ,FOREIGN KEY (link) REFERENCES LINKS(id)
);

create table broken_id (
  `what` VARCHAR(25),
  `id` INT,
  `check` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (what, id)
);

create table USERS (
  `id` INT,
  `links` INT default 0,
  `comments` INT default 0,
  `since` INT,
  `until` INT,
  `live` BOOLEAN default 1,
  PRIMARY KEY (id)
);

create table TAGS (
  `tag` INT,
  `link` INT,
  `status` TEXT,
  PRIMARY KEY (id, link)
);

commit;
