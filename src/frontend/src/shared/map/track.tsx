import * as React from "react";
import { Polyline, Popup, Rectangle } from "react-leaflet";
import { useQuery } from "react-query";
import { Button } from "reactstrap";
import { hashStringToColor } from "../../helpers/hash_strings";
import { AisTrack } from "../../models/ais_track";
import { config } from "../../helpers/constants";
import { CustomSpinner } from "../custom_spinner";
import { SettingsContext } from "../../providers/settings_provider";
import { seconds_to_timespan_string } from "../../helpers/time_span";

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
                                    <h3>{track.name ? track.name : track.callsign ? track.callsign : track.mmsi}</h3>
                                    <h5>Time</h5>
                                    <p>
                                        <b>Begin:</b> {new Date(track.begin_ts).toUTCString()}
                                        <br />
                                        <b>End:</b> {new Date(track.end_ts).toUTCString()}
                                        <br />
                                        <b>Duration:</b> {seconds_to_timespan_string((new Date(track.end_ts).getTime() - new Date(track.begin_ts).getTime()) / 1000)}
                                    </p>
                                    <h5>Extended information</h5>
                                    <p>
                                        <b>Destination:</b> {track.destination}
                                        <br />
                                        <b>Cargo type:</b> {track.cargo_type}
                                        <br />
                                        <b>ETA:</b> {track.eta ? new Date(track.eta).toUTCString() : "No ETA provided"}
                                        <br />
                                    </p>
                                    <h5>Ship information</h5>
                                    <p>
                                        <b>MMSI:</b> {track.mmsi}
                                        <br />
                                        <b>IMO:</b> {track.imo}
                                        <br />
                                        <b>Mobile type:</b> {track.mobile_type}
                                        <br />
                                        <b>Callsign:</b> {track.callsign}
                                        <br />
                                        <b>Name:</b> {track.name}
                                        <br />
                                        <b>Ship type:</b> {track.ship_type}
                                        <br />
                                        <b>Width:</b> {track.width}
                                        <br />
                                        <b>Length:</b> {track.length}
                                        <br />
                                        <b>Draught:</b> {track.draught}
                                        <br />
                                        <b>A:</b> {track.a}
                                        <br />
                                        <b>B:</b> {track.b}
                                        <br />
                                        <b>C:</b> {track.c}
                                        <br />
                                        <b>D:</b> {track.d}
                                        <br />
                                    </p>
                                </Popup>
                            </Polyline>
                        );
                    })}
                </>
            )}
        </SettingsContext.Consumer>
    );
};
