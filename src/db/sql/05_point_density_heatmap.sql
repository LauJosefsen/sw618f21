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

    INSERT INTO heatmap_point_density
	SELECT
		grid.i, grid.j, t.ship_type,
	    COUNT(p)/ST_Area(grid.geom,true)
	FROM grid
    JOIN points AS p ON ST_Contains(grid.geom, p.location)
    JOIN track AS t ON p.track_id = t.id
	GROUP BY grid.i, grid.j, t.ship_type;

    with max as (
        SELECT max(intensity) as intensity FROM heatmap_point_density
    )
    UPDATE heatmap_point_density as hmpd
    SET intensity = (hmpd.intensity / max.intensity) * 100
    FROM max;


    RETURN TRUE;
END
$BODY$;
