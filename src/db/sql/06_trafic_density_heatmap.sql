-- trafic_density_heatmap

CREATE TABLE IF NOT EXISTS heatmap_trafic_density
(
	i int,
	j int,
	FOREIGN KEY (i,j) REFERENCES grid(i, j) deferrable,
	ship_type varchar(50),
	intensity double precision,
    PRIMARY KEY (i,j,ship_type) deferrable
);

CREATE OR REPLACE FUNCTION public.generate_trafic_density_heatmap(
	)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    TRUNCATE heatmap_trafic_density;

    WITH time_difference AS (
        SELECT max(timestamp)-min(timestamp) as interval FROM points
    )
    INSERT INTO heatmap_trafic_density
	SELECT
		grid.i, grid.j, t.ship_type,
	    SUM(ST_NumGeometries(ST_ClipByBox2d(t.geom, grid.geom)))/
	        (ST_Area(grid.geom,true)*time_difference.interval)
	FROM track_with_geom AS t, grid
	GROUP BY grid.i, grid.j, t.ship_type;


    RETURN TRUE;
END
$BODY$;
