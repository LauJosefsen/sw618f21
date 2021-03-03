CREATE DATABASE ais;

\c ais

START TRANSACTION;

CREATE EXTENSION postgis;

CREATE TABLE public.data
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
	destination varchar(100),
	eta timestamp,
	data_src_type varchar(20),
	a double precision,
	b double precision,
	c double precision,
	d double precision
);

CREATE TABLE public.ais_course (
    id serial primary key,
    MMSI varchar(50),
    destination varchar(100),
    eta timestamp
);

CREATE INDEX mmsi_index ON public.ais_course(MMSI);

CREATE TABLE public.ais_points
(
    id serial primary key,
    MMSI int,
    timestamp timestamp,
    location geometry(point) not null,
    rot double precision,
    sog double precision,
    cog double precision,
    heading int,
    ais_course_id int,
    CONSTRAINT fk_ais_course
        FOREIGN KEY(ais_course_id) REFERENCES public.ais_course(id)
);

COMMIT;