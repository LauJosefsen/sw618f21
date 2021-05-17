-- trafic_density_heatmap

CREATE TABLE IF NOT EXISTS heatmap_trafic_density
(
	i int,
	j int,
	FOREIGN KEY (i,j) REFERENCES grid(i, j),
	ship_type varchar(50),
	intensity double precision,
    PRIMARY KEY (i,j,ship_type)
);

CREATE OR REPLACE FUNCTION public.generate_trafic_density_heatmap(
	)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    TRUNCATE heatmap_trafic_density;

    INSERT INTO heatmap_trafic_density
	SELECT
		grid.i, grid.j, t.ship_type,
	    SUM(ST_NumGeometries(ST_ClipByBox2d(t.geom, grid.geom)))/
	        ST_Area(grid.geom,true)
	FROM track_with_geom AS t, grid
	GROUP BY grid.i, grid.j, t.ship_type;

    with max as (
        SELECT max(intensity) as intensity FROM heatmap_trafic_density
    )
    UPDATE heatmap_trafic_density as hmtd
    SET intensity = (hmtd.intensity / max.intensity) * 100
    FROM max;


    RETURN TRUE;
END
$BODY$;
