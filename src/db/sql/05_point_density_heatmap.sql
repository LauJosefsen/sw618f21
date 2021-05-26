-- point_density_heatmap

CREATE TABLE IF NOT EXISTS heatmap_point_density
(
	i int,
	j int,
	FOREIGN KEY (i,j) REFERENCES grid(i, j) deferrable,
	ship_type varchar(50),
	intensity double precision,
    PRIMARY KEY (i,j,ship_type) deferrable
);
