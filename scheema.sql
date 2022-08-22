drop table if exists dl_paths;
drop table if exists unsuported_urls;
drop table if exists server;
drop table if exists queue;
drop table if exists jobs;

create table dl_paths (
	time int,
	method varchar(8), proto varchar(8),
	host varchar(255), port int, 
	file_path text, query text, username varchar(255), passwd varchar(255),
	blob_name varchar(256), json_headers blob, status varchar(256)
);

create table unsuported_urls (url text);

create index url on dl_paths (method, proto, `host`(50), port, `file_path`(50), `query`(50), username, passwd);
create index time on dl_paths (time);
create index server on dl_paths (port, host);

create table queue (
	jobid varchar(255),
	method varchar(255),
	full text
);

create index url on queue (`full`(100));
create index job on queue (jobid);

create table jobs (
	jobid varchar(255),
	hostname varchar(255)
);

create index jobid on jobs (jobid);
