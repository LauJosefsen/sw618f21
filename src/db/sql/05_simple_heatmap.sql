CREATE MATERIALIZED VIEW public.heatmap_10m AS
    SELECT grid_point, count(*) FROM
        (
            SELECT
            ST_Transform(ST_SnapToGrid(ST_Transform(location, 3857), 10),4326) as grid_point
            FROM points
            WHERE sog > 1
        )
    AS grid
    GROUP BY grid_point;

CREATE INDEX heatmap_10m_geom_index
  ON heatmap_10m
  USING GIST (grid_point);
