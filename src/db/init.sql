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

CREATE INDEX mmsi_index ON public.data(MMSI);

CREATE TABLE public.ais_course (
    MMSI int,
    MMSI_split int,
    destination varchar(100),
    eta timestamp,
    PRIMARY KEY (MMSI, MMSI_split)
);

CREATE TABLE public.ais_points
(
    id serial primary key,
    MMSI int,
    MMSI_split int,
    timestamp timestamp,
    location geometry(point) not null,
    rot double precision,
    sog double precision,
    cog double precision,
    heading int,
    CONSTRAINT fk_ais_course
        FOREIGN KEY(MMSI,MMSI_split) REFERENCES public.ais_course(MMSI, MMSI_split)
);

CREATE INDEX ais_course_id_index ON public.ais_points(MMSI, MMSI_split);
CREATE INDEX ais_course_timestamp_index ON public.ais_points(timestamp);

COMMIT;