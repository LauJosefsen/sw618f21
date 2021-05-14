CREATE MATERIALIZED VIEW public.simple_heatmap AS
    SELECT grid_point, ship_type, count(*) FROM
        (
            SELECT
            ship_type,
            ST_Transform(ST_SnapToGrid(ST_Transform(location, 25832), 10),4326) as grid_point
            FROM points
            JOIN track AS t on points.track_id = t.id
            WHERE sog > 1
        )
    AS grid
    GROUP BY grid_point, ship_type;

CREATE INDEX IF NOT EXISTS simple_heatmap_geom_index
  ON simple_heatmap
  USING GIST (grid_point);
