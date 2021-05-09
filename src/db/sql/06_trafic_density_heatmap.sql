-- trafic_density_heatmap
CREATE TABLE IF NOT EXISTS grid(
    i int,
    j int,
    geom geometry,
    PRIMARY KEY (i,j)
);

CREATE INDEX IF NOT EXISTS grid_geom_index
 ON grid
 USING GIST (geom);

CREATE TABLE IF NOT EXISTS heatmap_trafic_density
(
	i int,
	j int,
	FOREIGN KEY (i,j) REFERENCES grid(i, j),
	ship_type varchar(50),
	intensity int,
    PRIMARY KEY (i,j,ship_type)
);

CREATE OR REPLACE FUNCTION public.create_grid(grid_size_meters int)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
BEGIN
    TRUNCATE grid CASCADE;

        INSERT INTO grid
        SELECT i, j, ST_Transform(geom, 4326) as geom
        FROM
        (
            SELECT
            (
                ST_SquareGrid(grid_size_meters, ST_Transform(location, 3857))
            ).* as geom
            FROM
            (
                SELECT location FROM enc_cells ORDER BY ST_Area(location) DESC LIMIT 1
            ) as enc
        ) as grid_bounds;
    RETURN TRUE;
END
$BODY$;





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
	    SUM(ST_NumGeometries(ST_ClipByBox2d(t.geom, grid.geom)))
	FROM track_with_geom AS t, grid
	GROUP BY grid.i, grid.j, t.ship_type;

    RETURN TRUE;
END
$BODY$;
