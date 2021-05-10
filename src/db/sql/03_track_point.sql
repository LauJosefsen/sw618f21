CREATE TABLE public.track
(
    id          bigserial primary key,
    destination varchar(100),
    cargo_type  varchar(50),
    eta         timestamp,
    MMSI        int,
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

CREATE INDEX point_geom_index
  ON points
  USING GIST (location);

CREATE INDEX point_track ON points (track_id ASC NULLS FIRST);

-- View: public.track_with_geom
CREATE MATERIALIZED VIEW public.track_with_geom
AS
    SELECT
        t.*,
        st_makeline(p.location ORDER BY p.timestamp) AS geom,
        min(p.timestamp) as begin_ts,
        max(p.timestamp) as end_ts
    FROM track t
    JOIN points p ON p.track_id = t.id
    GROUP BY t.id;

CREATE INDEX track_with_geom_index
  ON track_with_geom
  USING GIST (geom);

