import * as React from 'react';
import L from 'leaflet'
import 'leaflet.heat';
import { Popup, Rectangle, useMap } from "react-leaflet";
import { useEffect } from "react";
import { useQuery } from 'react-query';
import { Button, Spinner } from 'reactstrap';
import { EncCell } from '../../models/enc_cells';
import { SettingsContext } from '../../providers/settings_provider';
import { CustomSpinner } from '../custom_spinner';

interface Props {
    enc_cell_id: number
}

export const SimpleHeatMap = (props: Props) => {

    const { isLoading: loading_enc, error: error_enc, data: data_heatmap } = useQuery(`repoHeatMapGrid_${props.enc_cell_id}`, () =>
        fetch(`http://localhost:5000/cluster-heatmap?enc_cell_id=${props.enc_cell_id}`).then(res =>
            res.json()
        ));

    const [heatMapLayer, setHeatMapLayer] = React.useState<any>();

    const map = useMap()
    useEffect(() => {
        console.log("Refreshed heatmaplayer")
        setHeatMapLayer(L.heatLayer(data_heatmap ? data_heatmap.heatmap_data : [], { radius: 10 }))
    }, [data_heatmap])

    useEffect(() => {
        console.log("1 heatmaplayer")
        if (heatMapLayer) {
            console.log("2 heatmaplayer")
            heatMapLayer.addTo(map)
        }
    }, [heatMapLayer])

    if (!data_heatmap) return <CustomSpinner message="Loading heatmap layer" />

    return (

        <SettingsContext.Consumer>
            {({ settings, setSettings }) => (
                <>
                    <Rectangle bounds={
                        [
                            [data_heatmap.enc.location.coordinates[0][0][0], data_heatmap.enc.location.coordinates[0][0][1]],
                            [data_heatmap.enc.location.coordinates[0][2][0], data_heatmap.enc.location.coordinates[0][2][1]]
                        ]} pathOptions={{ color: "black" }}>
                        <Popup>
                            <h3>
                                {data_heatmap.enc.cell_title}
                            </h3>
                            <p>
                                {data_heatmap.enc.cell_name}
                            </p>
                            <Button onClick={() => {
                                map.removeLayer(heatMapLayer)
                                setSettings({ ...settings, encIdForHeatMap: undefined, showEnc: true })
                            }}>Exit heatmap-layer</Button>
                        </Popup>
                    </Rectangle>
                </>
            )}



        </SettingsContext.Consumer>


    )
}