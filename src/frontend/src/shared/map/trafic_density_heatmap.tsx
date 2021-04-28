import * as React from "react";
import L from "leaflet";
import "leaflet.heat";
import { Popup, Rectangle, useMap } from "react-leaflet";
import { useEffect } from "react";
import { useQuery } from "react-query";
import { Button } from "reactstrap";
import { SettingsContext } from "../../providers/settings_provider";
import { CustomSpinner } from "../custom_spinner";
import { config } from "../../helpers/constants";

interface Props {
    enc_cell_id: number;
    ship_types: string[];
}

export const TraficDensityHeatMap = (props: Props) => {
    const { isLoading: loading, error, data: data_heatmap } = useQuery(["trafic_density_heatmap", props.enc_cell_id, props.ship_types], () =>
        fetch(`${config.api_url}/heatmaps/trafic_dwdwensity?enc_cell_id=${props.enc_cell_id}&ship_types=${props.ship_types.toString()}`).then((res) => res.json())
    );

    const [heatMapLayer, setHeatMapLayer] = React.useState<any>();

    const map = useMap();
    useEffect(() => {
        setHeatMapLayer(L.heatLayer(data_heatmap ? data_heatmap.heatmap_data : [], { radius: 10, blur: 0, max: 1 }));
    }, [data_heatmap]);

    useEffect(() => {
        if (heatMapLayer) {
            heatMapLayer.addTo(map);
        }
    }, [heatMapLayer, map]);

    if (!data_heatmap || loading || error) return <CustomSpinner message="Loading heatmap layer" />;

    return (
        <SettingsContext.Consumer>
            {({ settings, setSettings }) => (
                <>
                    <Rectangle
                        bounds={[
                            [data_heatmap.enc.location.coordinates[0][0][0], data_heatmap.enc.location.coordinates[0][0][1]],
                            [data_heatmap.enc.location.coordinates[0][2][0], data_heatmap.enc.location.coordinates[0][2][1]],
                        ]}
                        pathOptions={{ color: "black" }}
                    >
                        <Popup>
                            <h3>{data_heatmap.enc.cell_title}</h3>
                            <p>{data_heatmap.enc.cell_name}</p>
                            <Button
                                onClick={() => {
                                    map.removeLayer(heatMapLayer);
                                    setSettings({ ...settings, encIdForHeatMap: undefined, showEnc: true });
                                }}
                            >
                                Exit heatmap-layer
                            </Button>
                        </Popup>
                    </Rectangle>
                </>
            )}
        </SettingsContext.Consumer>
    );
};
