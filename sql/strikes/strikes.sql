create table STRIKES (
  `link` INT,
  `comment` INT,
  `user_id` INT,
  `date` DATETIME,
  `reason` VARCHAR(50),
  PRIMARY KEY (comment),
  FOREIGN KEY (link) REFERENCES LINKS(id),
  FOREIGN KEY (comment) REFERENCES COMMENTS(id)
);
