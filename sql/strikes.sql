create table STRIKES (
  `link` INT,
  `comment` INT,
  `reason` VARCHAR(50),
  PRIMARY KEY (comment),
  FOREIGN KEY (link) REFERENCES LINKS(id),
  FOREIGN KEY (comment) REFERENCES COMMENTS(id)
);
