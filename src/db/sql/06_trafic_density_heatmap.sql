-- trafic_density_heatmap
CREATE TABLE IF NOT EXISTS grid(
    i int,
    j int,
    geom geometry,
    PRIMARY KEY (i,j)
);

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
    TABLE_RECORD RECORD;
    CNT          BIGINT;
BEGIN
    TRUNCATE grid;

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
DECLARE
    TABLE_RECORD RECORD;
    GRID_INTERSECTS RECORD;
    CNT          BIGINT;
BEGIN
    -- noinspection SqlWithoutWhere
    UPDATE heatmap_trafic_density SET intensity = 0;

    FOR TABLE_RECORD IN
		SELECT
		    s.ship_type as ship_type
		    geom
		FROM track_with_geom as t
        JOIN ship AS s on s.mmsi = t.ship_mmsi
        LOOP
            INSERT INTO heatmap_trafic_density
            SELECT
                i, j, TABLE_RECORD.geom, 1
            FROM grid
            WHERE
                  ST_Intersects(
						geom,
						TABLE_RECORD.geom
					)
            ON CONFLICT DO UPDATE SET intensity = intensity + 1;


--             LOOP
--                 SELECT count(*)
--                 INTO CNT FROM heatmap_trafic_density
--                 WHERE
--                     i = GRID_INTERSECTS.i AND
--                     j = GRID_INTERSECTS.j AND
--                     ship_type = TABLE_RECORD.ship_type;
--
--                 IF CNT == 0 THEN
--                     INSERT INTO heatmap_trafic_density
--                         (i, j, ship_type, intensity)
--                         VALUES (
--                                 GRID_INTERSECTS.i,
--                                 GRID_INTERSECTS.j,
--                                 TABLE_RECORD.ship_type,
--                                 1
--                                 );
--                 ELSE
--                     UPDATE heatmap_trafic_density
--                         SET intensity = intensity + 1
--                         WHERE
--                               ship_type = TABLE_RECORD.ship_type AND
--                               i = GRID_INTERSECTS.i AND
--                               j = GRID_INTERSECTS.j;
--                 END IF;
--             END LOOP;
        END LOOP;

    RETURN TRUE;
END
$BODY$;
