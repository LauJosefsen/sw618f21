CREATE DATABASE ais;

\c ais

START TRANSACTION;

CREATE EXTENSION postgis;

CREATE TABLE public.data
(
    timestamp                   timestamp not null,
    mobile_type                 varchar(50),
    MMSI                        int,
    latitude                    double precision,
    longitude                   double precision,
    nav_stat                    varchar(50),
    rot                         double precision,
    sog                         double precision,
    cog                         double precision,
    heading                     double precision,
    imo                         varchar(10),
    callsign                    varchar(10),
    name                        text,
    ship_type                   varchar(50),
    cargo_type                  varchar(50),
    width                       double precision,
    length                      double precision,
    position_fixing_device_type varchar(50),
    draught                     double precision,
    destination                 varchar(100),
    eta                         timestamp,
    data_src_type               varchar(20),
    a                           double precision,
    b                           double precision,
    c                           double precision,
    d                           double precision,
    is_processed                bool DEFAULT False
);

CREATE INDEX mmsi_index ON public.data (MMSI);

CREATE TABLE public.ship
(
    MMSI        int PRIMARY KEY,
    IMO         varchar(10),
    mobile_type varchar(50),
    callsign    varchar(10),
    name        text,
    ship_type   varchar(50),
    width       double precision,
    length      double precision,
    draught     double precision,
    a           double precision,
    b           double precision,
    c           double precision,
    d           double precision
);

CREATE TABLE public.track
(
    id          bigserial primary key,
    ship_mmsi   int,
    destination varchar(100),
    cargo_type  varchar(50),
    eta         timestamp,
    CONSTRAINT fk_track_ship
        FOREIGN KEY (ship_mmsi) REFERENCES public.ship (mmsi)
);

CREATE TABLE public.points
(
    id                          bigserial primary key,
    track_id                    bigint,
    timestamp                   timestamp,
    location                    geometry(point) not null,
    rot                         double precision,
    sog                         double precision,
    cog                         double precision,
    heading                     int,
    position_fixing_device_type varchar(50),
    CONSTRAINT fk_ais_track
        FOREIGN KEY (track_id) REFERENCES public.track (id)
);

CREATE INDEX track_timestamp_index ON public.points (timestamp);

CREATE TABLE public.enc_cells
(
    cell_name    varchar(50) primary key,
    cell_title   text,
    edition      int,
    edition_date date,
    update       int,
    update_date  date,
    location     geometry(polygon) not null
);

COMMIT;