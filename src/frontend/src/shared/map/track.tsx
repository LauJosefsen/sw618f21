import { SIGHUP } from 'node:constants';
import * as React from 'react';
import { Marker, Polyline, Popup } from 'react-leaflet';
import { useQuery } from 'react-query';
import { Spinner } from 'reactstrap';
import { hashStringToColor } from '../../helpers/hash_strings';
import { AisTrack } from '../../models/ais_track';

interface Props {
    limit: number;
    offset: number;
    search: string;
}

export const MapTrack = (props: Props) => {
    const { isLoading, error, data } = useQuery(`repoTrackData-${props.limit}-${props.offset}-${props.search}`, () =>
        fetch(`http://localhost:5000/tracks?limit=${props.limit}&offset=${props.offset}&search=${props.search}`).then(res =>
            res.json()
        ));

    if (error) return <>'An error has occurred: ' + error</>


    if (isLoading) return <Spinner />

    // TODO: Draw tracks on leaflet..
    return <>
        {data.map((track: AisTrack) => {
            return (
                <Polyline key={track.id} positions={track.coordinates} color={hashStringToColor(track.mmsi+"")}>
                    <Popup>
                        <h3>
                            {track.mmsi}
                        </h3>
                        <p>
                            Begin: {(new Date(track.timestamp_begin)).toLocaleString()}
                        </p>
                        <p>
                            End: {(new Date(track.timestamp_end)).toLocaleString()}
                        </p>
                    </Popup>
                </Polyline>
            )
        })}
    </>;
}