select id from COMMENTS where user_id is null order by id INTO OUTFILE '/tmp/cmt_user_id.txt';
select id from LINKS where user_id is null order by id INTO OUTFILE '/tmp/lnk_user_id.txt';
select id from USERS where `create` is null order by id INTO OUTFILE '/tmp/user_create.txt';
select id from USERS where `create` is not null and (live is null or live=1) order by id INTO OUTFILE '/tmp/user_live.txt';

