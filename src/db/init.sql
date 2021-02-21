CREATE DATABASE ais;


\c ais

CREATE SCHEMA ais;

CREATE TABLE ais.data
(
	timestamp timestamp not null,
	mobile_type varchar(50),
	MMSI int,
	latitude double precision,
	longitude double precision,
	nav_stat varchar(50),
	rot double precision,
	sog double precision,
	cog double precision,
	heading double precision,
	imo varchar(50),
	callsign varchar(10),
	name text,
	ship_type varchar(50),
	cargo_type varchar(50),
	width double precision,
	length double precision,
	position_fixing_device_type varchar(50),
	draught double precision,
	eta timestamp,
	data_src_type varchar(20),
	destination varchar(100),
	a double precision,
	b double precision,
	c double precision,
	d double precision,
	constraint data_pk
		primary key (timestamp, MMSI)
);