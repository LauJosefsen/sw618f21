CREATE TABLE IF NOT EXISTS public.max_draught_map
(
    i integer NOT NULL,
    j integer NOT NULL,
    min_depth double precision,
    PRIMARY KEY (i, j)
);


CREATE TABLE IF NOT EXISTS public.interpolated_depth
(
    i integer NOT NULL,
    j integer NOT NULL,
    depth double precision,
    varians double precision,
    PRIMARY KEY (i, j),
    FOREIGN KEY (i,j) REFERENCES grid(i,j)
);


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




-- FUNCTION: public.get_tile_grids(integer, integer)
CREATE OR REPLACE FUNCTION public.get_tile_grids(
	min_zoom integer,
	max_zoom integer)
    RETURNS TABLE(z integer, x integer, y integer, geom geometry)
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE z int;
DECLARE x int;
DECLARE y int;
DECLARE largest_enc record;
DECLARE grid_size int;

BEGIN
	CREATE TEMPORARY TABLE IF NOT EXISTS tile_grids(
		z int,
		x int,
		y int,
		geom geometry
	);
	TRUNCATE TABLE tile_grids;

	SELECT location INTO largest_enc FROM enc_cells ORDER BY ST_Area(location) DESC LIMIT 1;
	FOR z IN min_zoom..max_zoom
	LOOP
		grid_size = POWER(2,z);
		FOR x IN 0..grid_size-1
		LOOP
			FOR y IN 0..grid_size-1
			LOOP
				IF ST_Intersects(largest_enc.location, ST_Transform(ST_TileEnvelope(z,x,y), 4326)) THEN
					INSERT INTO tile_grids VALUES (z,x,y,ST_Transform(ST_TileEnvelope(z,x,y),3857));
				END IF;
			END LOOP;
		END LOOP;
	END LOOP;

	return query SELECT * FROM tile_grids;
END
$BODY$;
