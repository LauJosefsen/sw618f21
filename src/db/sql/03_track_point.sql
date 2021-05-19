CREATE TABLE public.ship
(
    id          bigserial primary key,
    MMSI        int,
    IMO         text,
    mobile_type text,
    callsign    text,
    name        text,
    ship_type   text,
    width       double precision,
    length      double precision,
    a           double precision,
    b           double precision,
    c           double precision,
    d           double precision,
    CONSTRAINT ship_mmsi_imo_mobile_type_callsign_name_ship_type_width_len_key UNIQUE(mmsi, imo, mobile_type, callsign, name, ship_type, width, length, a, b, c, d)
);


CREATE TABLE public.track
(
    id          bigserial primary key,
    ship_id     bigint,
    FOREIGN KEY (ship_id) REFERENCES ship(id),
    destination text,
    cargo_type  text,
    eta         timestamp,
    draught     double precision
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
    position_fixing_device_type text,
    FOREIGN KEY (track_id) REFERENCES public.track (id)
);

CREATE INDEX track_timestamp_index ON public.points (timestamp);

CREATE INDEX point_geom_index
  ON points
  USING GIST (location);

CREATE INDEX point_track_id ON points (track_id ASC NULLS FIRST);
CREATE INDEX track_ship_id ON track (ship_id ASC NULLS FIRST);

CREATE INDEX ship_id ON ship (id ASC NULLS FIRST);
CREATE INDEX track_id ON track (id ASC NULLS FIRST);

-- View: public.track_with_geom
CREATE MATERIALIZED VIEW public.track_with_geom
AS
    SELECT
        t.*,
        ST_Transform(ST_Simplify(ST_Transform(st_makeline(p.location ORDER BY p."timestamp"), 25832),5), 4326) AS geom,
        min(p.timestamp) as begin_ts,
        max(p.timestamp) as end_ts
    FROM track t
    JOIN points p ON p.track_id = t.id
    GROUP BY t.id;

CREATE INDEX track_with_geom_index
  ON track_with_geom
  USING GIST (geom);

