create table broken_id (
  "what" TEXT,
  "id" NUMBER,
  "check" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (what, id)
);
