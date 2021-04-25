-- trafic_density_heatmap
CREATE TABLE IF NOT EXISTS heatmap_trafic_density_1000m
(
	i int,
	j int,
	geom geometry,
	intensity int,
	PRIMARY KEY (i,j)
);

CREATE OR REPLACE FUNCTION public.generate_trafic_density_heatmap(
	)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    TABLE_RECORD RECORD;
    CNT          BIGINT;
BEGIN
    select count(*) into CNT from heatmap_trafic_density_10m;

    -- if table is empty, insert grid
    if cnt == 0 then
        INSERT INTO heatmap_trafic_density_10m
        SELECT ST_Transform(geom, 4326) as geom, 0
        FROM
        (
            SELECT
            (
                ST_SquareGrid(100, ST_Transform(location, 3857))
            ).* as geom
            FROM
            (
                SELECT location FROM enc_cells ORDER BY ST_Area(location) DESC LIMIT 1
            ) as enc
        ) as grid_bounds;
    else
        -- noinspection SqlWithoutWhere
        UPDATE heatmap_trafic_density_10m SET intensity = 0;
    end if;


    FOR TABLE_RECORD IN
		SELECT geom FROM track_with_geom

        LOOP
            UPDATE heatmap_trafic_density_10m
				SET intensity = intensity + 1
				WHERE ST_Intersects(
						geom,
						TABLE_RECORD.geom
					);

        END LOOP;

    RETURN TRUE;
END
$BODY$;
