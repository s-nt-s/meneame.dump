create table IF NOT EXISTS USERS (
  `id` INT,
  `links` INT default 0,
  `comments` INT default 0,
  `posts` INT default 0,
  `create` DATE,
  `since` DATE,
  `until` DATE,
  `live` BOOLEAN default 1,
  PRIMARY KEY (id)
);

insert ignore into USERS (id)
select distinct user_id from (
  select user_id from LINKS
  union
  select user_id from COMMENTS
  union
  select user_id from POSTS
) T where user_id is not null
;

update USERS set live=0 where live=1 and id in (
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
    from_unixtime(min(d)) min_date,
    from_unixtime(max(d)) max_date,
    sum(link) links,
    sum(comment) comments,
    sum(posts) posts
  from (
    select user_id, sent_date d, 1 link, 0 comment, 0 posts from LINKS
    union
    select user_id, `date` d, 0 link, 1 comment, 0 posts from COMMENTS
    union
    select user_id, `date` d, 0 link, 0 comment, 1 posts from POSTS
  ) AUX0 where
    user_id is not null
  group by
    user_id
) AUX on USERS.id = AUX.user_id
set
  USERS.since = AUX.min_date,
  USERS.until = AUX.max_date,
  USERS.links = AUX.links,
  USERS.comments = AUX.comments,
  USERS.posts = AUX.posts
;
