CREATE OR REPLACE FUNCTION public.generate_depth_map(
	)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    TRUNCATE max_draught_map;
    INSERT INTO max_draught_map
    SELECT
        grid.i, grid.j, max(t.draught)
    FROM grid
    JOIN track_with_geom  AS t ON ST_Intersects(grid.geom,t.geom)
    GROUP BY grid.i, grid.j;

    DELETE FROM max_draught_map WHERE min_depth is null;

    RETURN TRUE;
END
$BODY$;