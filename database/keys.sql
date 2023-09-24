create table keys (
	uuid UUID not NUll,
	server VARCHAR not null,
	server_port INTEGER not null,
	password VARCHAR not null,
	method VARCHAR not null,
	name VARCHAR not null,
	is_active BOOLEAN not null,
	PRIMARY KEY (uuid, name)
);