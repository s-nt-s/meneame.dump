insert ignore into USERS (id)
select distinct user_id from (
  select user_id from LINKS
  union
  select user_id from COMMENTS
) T where user_id is not null
;

update USERS set live=0 where id in (
  select user_id from (
    select user_id, user from LINKS
    union
    select user_id, user from COMMENTS
  ) T where user_id is not null and user like '--%--'
);

update USERS
inner join (
  select
    user_id,
    count(*) C,
    min(sent_date) min_date,
    max(sent_date) max_date
  from
    LINKS
  where
    user_id is not null
  group by
    user_id
) AUX on USERS.id = AUX.user_id
set
  USERS.links = AUX.C,
  USERS.since = AUX.min_date,
  USERS.until = AUX.max_date
;

update USERS
inner join (
  select
    user_id,
    count(*) C,
    min(`date`) min_date,
    max(`date`) max_date
  from
    COMMENTS
  where
    user_id is not null
  group by
    user_id
) AUX on USERS.id = AUX.user_id
set
  USERS.comments = AUX.C,
  USERS.since = CASE
    when AUX.min_date is null then USERS.since
    when USERS.since is null then AUX.min_date
    when AUX.min_date<USERS.since then AUX.min_date
    else USERS.since
  END,
  USERS.until = CASE
    when AUX.max_date is null then USERS.until
    when USERS.until is null then AUX.max_date
    when AUX.max_date>USERS.until then AUX.max_date
    else USERS.until
  END
;
