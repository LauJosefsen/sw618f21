-- point_density_heatmap

CREATE TABLE IF NOT EXISTS heatmap_point_density
(
	i int,
	j int,
	FOREIGN KEY (i,j) REFERENCES grid(i, j),
	ship_type varchar(50),
	intensity double precision,
    PRIMARY KEY (i,j,ship_type)
);

CREATE OR REPLACE FUNCTION public.generate_point_density_heatmap(
	)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    TRUNCATE heatmap_point_density;

    WITH time_difference AS (
        SELECT max(timestamp)-min(timestamp) as interval FROM points
    )
    INSERT INTO heatmap_point_density
	SELECT
		grid.i, grid.j, t.ship_type,
	    COUNT(p)/(ST_Area(grid.geom,true)*time_difference.interval)
	FROM grid
    JOIN points AS p ON ST_Contains(grid.geom, p.location)
    JOIN track AS t ON p.track_id = t.id
	GROUP BY grid.i, grid.j, t.ship_type;

    RETURN TRUE;
END
$BODY$;
