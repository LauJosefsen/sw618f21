import * as React from 'react';
import { Marker, Polyline, Popup } from 'react-leaflet';
import { useQuery } from 'react-query';
import { Spinner } from 'reactstrap';
import icon from 'leaflet/dist/images/marker-icon.png';
import * as L from 'leaflet';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import {config} from "../../helpers/constants";

interface Props {
}

export const MapPoints = (props: Props) => {

    let DefaultIcon = L.icon({
        iconUrl: icon,
        shadowUrl: iconShadow
    });
    
    const { isLoading, error, data } = useQuery(`repoPointData`, () =>
        fetch(`${config.api_url}/cluster-heatmap`).then(res =>
            res.json()
        ));

    if (error) return <>'An error has occurred: ' + error</>


    if (isLoading) return <Spinner />

    // TODO: Draw tracks on leaflet..
    return <>
        {data.coordinates.map((point: [number,number]) => {
            return (
                <Marker position={point} icon={DefaultIcon}>
                </Marker>
            )
        })}
    </>;
}