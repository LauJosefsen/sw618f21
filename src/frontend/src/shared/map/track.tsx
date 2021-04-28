import * as React from "react";
import { Polyline, Popup, Rectangle } from "react-leaflet";
import { useQuery } from "react-query";
import { Button, Spinner } from "reactstrap";
import { hashStringToColor } from "../../helpers/hash_strings";
import { AisTrack } from "../../models/ais_track";
import { config } from "../../helpers/constants";
import { CustomSpinner } from "../custom_spinner";
import { map } from "leaflet";
import { SettingsContext } from "../../providers/settings_provider";

interface Props {
    enc_cell_id: number;
    ship_types: string[];
}

export const MapTrack = (props: Props) => {
    const { isLoading, error, data } = useQuery(["tracks_in_enc", props.enc_cell_id, props.ship_types], () =>
        fetch(`${config.api_url}/tracks/get_by_enc_id?enc_cell_id=${props.enc_cell_id}&ship_types=${props.ship_types.toString()}`).then((res) => res.json())
    );

    if (error || isLoading) return <CustomSpinner message="Loading tracks..." />;

    return (
        <SettingsContext.Consumer>
            {({ settings, setSettings }) => (
                <>
                    <Rectangle
                        bounds={[
                            [data.enc.location.coordinates[0][0][0], data.enc.location.coordinates[0][0][1]],
                            [data.enc.location.coordinates[0][2][0], data.enc.location.coordinates[0][2][1]],
                        ]}
                        pathOptions={{ color: "black" }}
                    >
                        <Popup>
                            <h3>{data.enc.cell_title}</h3>
                            <p>{data.enc.cell_name}</p>
                            <Button
                                onClick={() => {
                                    setSettings({ ...settings, encIdForTrack: undefined, showEnc: true });
                                }}
                            >
                                Exit track-layer
                            </Button>
                        </Popup>
                    </Rectangle>
                    {data.tracks.map((track: AisTrack) => {
                        return (
                            <Polyline key={track.id} positions={track.coordinates} color={hashStringToColor(track.mmsi + "")}>
                                <Popup>
                                    <h3>{track.mmsi}</h3>
                                    <p>Begin: {new Date(track.timestamp_begin).toLocaleString()}</p>
                                    <p>End: {new Date(track.timestamp_end).toLocaleString()}</p>
                                </Popup>
                            </Polyline>
                        );
                    })}
                </>
            )}
        </SettingsContext.Consumer>
    );
};
