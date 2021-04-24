-- trafic_density_heatmap
CREATE TABLE IF NOT EXISTS heatmap_trafic_density_1000m
(
	i int,
	j int,
	geom geometry,
	intensity int,
	PRIMARY KEY (i,j)
);

INSERT INTO heatmap_trafic_density_1000m
SELECT
i, j, ST_Transform(geom, 4326) as geom, 0
FROM
(
	SELECT
	(
		ST_SquareGrid(10000, ST_Transform(location, 3857))
	).* as geom
	FROM
	(
		SELECT location FROM enc_cells ORDER BY ST_Area(location) DESC LIMIT 1
	) as enc
) as grid_bounds ORDER BY i asc;

UPDATE heatmap_trafic_density_1000m
SET intensity = intensity + 1
WHERE ST_Intersects(
	geom,
	(SELECT line.geom FROM line))
