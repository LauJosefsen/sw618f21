CREATE TABLE IF NOT EXISTS grid(
    i int,
    j int,
    geom geometry,
    PRIMARY KEY (i,j)
);
CREATE TABLE IF NOT EXISTS grid_size(
    size int
);

CREATE INDEX IF NOT EXISTS grid_geom_index
 ON grid
 USING GIST (geom);

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
            ST_SquareGrid(grid_size_meters, ST_Transform(location, 25832))
        ).* as geom
        FROM
        (
            SELECT location FROM enc_cells ORDER BY ST_Area(location) DESC LIMIT 1
        ) as enc
    ) as grid_bounds;

    TRUNCATE grid_size;
    INSERT INTO grid_size (size) VALUES (grid_size_meters);

    RETURN TRUE;
END
$BODY$;