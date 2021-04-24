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
    d                           double precision
);

CREATE INDEX mmsi_index ON public.data (MMSI);

CREATE TABLE public.data_error_rate
(
    rule_name          varchar(100) primary key,
    mmsi_count_before  int,
    mmsi_count_after   int,
    point_count_before int,
    point_count_after  int
);