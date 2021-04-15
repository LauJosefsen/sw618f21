import * as React from 'react';
import { Popup, Rectangle } from 'react-leaflet';
import { useQuery } from 'react-query';
import { Button, Spinner } from 'reactstrap';
import { hashStringToColor } from '../../helpers/hash_strings';
import { EncCell } from '../../models/enc_cells';
import * as L from 'leaflet';
import { CustomSpinner } from '../custom_spinner';

interface Props {
}

export const MapHeatMapGrid = (props: Props) => {

    const convertTo4326 = (rect_list: any) => {

        rect_list.forEach((rect: any) => {
            console.log("map3", rect)
            rect.coordinates[0].forEach((coords: any) =>{
                console.log("map", coords)
                coords = L.Projection.SphericalMercator.unproject(coords);
                console.log("map2", coords)
            })
        });     
        return rect_list 
    }

    const { isLoading: loading_enc, error: error_enc, data: data_enc } = useQuery(`repoHeatMapGrid`, () =>
        fetch(`http://localhost:5000/cluster-heatmap`).then(res =>
            res.json()
        ));

    if (error_enc || error_enc) return <>'An error has occurred: ' + error</>


    if (loading_enc || !data_enc) return <CustomSpinner />


    return (<>
        {data_enc.map((rect: any) => {
            return (<>
                <Rectangle bounds={rect.coordinates[0]} pathOptions={{ color: "black" }}>
                    <Popup>
                        <Button>Show tracks in cell</Button>
                    </Popup>
                </Rectangle>
            </>

            )
        })}</>);
}