CREATE TABLE IF NOT EXISTS public.max_draught_map
(
    i integer NOT NULL,
    j integer NOT NULL,
    min_depth double precision,
    PRIMARY KEY (i, j) deferrable,
    FOREIGN KEY (i,j) REFERENCES grid(i,j) deferrable
);


CREATE TABLE IF NOT EXISTS public.interpolated_depth
(
    i integer NOT NULL,
    j integer NOT NULL,
    depth double precision,
    varians double precision,
    PRIMARY KEY (i, j) deferrable,
    FOREIGN KEY (i,j) REFERENCES grid(i,j) deferrable
);

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

CREATE OR REPLACE FUNCTION public.get_downscaled_raw_depth_map(
	downscale_ratio int
)
    RETURNS TABLE(geom geometry, depth double precision )
    LANGUAGE 'plpgsql'
AS $BODY$
DECLARE i int;
DECLARE j int;
DECLARE y int;
DECLARE grid_bounds record;

BEGIN
	CREATE TEMPORARY TABLE IF NOT EXISTS downscaled_raw_depth_map(
		geom geometry, depth double precision
	);
	TRUNCATE TABLE downscaled_raw_depth_map;

	SELECT
		min(grid.i) as min_i,
		max(grid.i) as max_i,
		min(grid.j) as min_j,
		max(grid.j) as max_j
	INTO grid_bounds
	FROM grid;

	FOR i_loop IN grid_bounds.min_i..grid_bounds.max_i by downscale_ratio
	LOOP
		FOR j_loop IN grid_bounds.min_j..grid_bounds.max_j by downscale_ratio
		LOOP
			INSERT INTO downscaled_raw_depth_map
			SELECT ST_Union(grid.geom), max(min_depth)
			FROM max_draught_map RIGHT JOIN grid ON max_draught_map.i = grid.i AND max_draught_map.j = grid.j
			WHERE grid.i >= i_loop AND grid.i < i_loop+downscale_ratio AND grid.j>= j_loop AND grid.j < j_loop+downscale_ratio HAVING max(min_depth) IS NOT null;
		END LOOP;
	END LOOP;

	return query SELECT * FROM downscaled_raw_depth_map;
END
$BODY$;
