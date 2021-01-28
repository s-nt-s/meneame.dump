UPDATE
  STRIKES S INNER JOIN COMMENTS C on S.comment = C.id
SET
  S.user_id = C.user_id,
  S.`date` = from_unixtime(C.`date`)
WHERE S.user_id is null or S.`date` is null;
