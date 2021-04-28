import { Popup, Rectangle } from "react-leaflet";
import { useQuery } from "react-query";
import { Button, Col, Row } from "reactstrap";
import { hashStringToColor } from "../../helpers/hash_strings";
import { EncCell } from "../../models/enc_cells";
import { SettingsContext } from "../../providers/settings_provider";
import { CustomSpinner } from "../custom_spinner";
import { config } from "../../helpers/constants";
import React, { useState } from "react";
import { CustomMultiSelect } from "../custom_multi_select";
import { make_options } from "../../helpers/make_options";

interface Props {
    bounds: { [key: string]: [boolean, number, number] };
    search: string;
}

export const MapEncCells = (props: Props) => {
    const getBoundsString = (bounds: { [key: string]: [boolean, number, number] }): string => {
        let str_buf = "";
        for (let key in bounds) {
            let value = bounds[key];
            if (value[0]) str_buf += `${value[1]},${value[2]},`;
        }
        str_buf = str_buf.slice(0, str_buf.length - 1);
        console.log(str_buf);
        return str_buf;
    };
    const { isLoading: loading_enc, error: error_enc, data: data_enc } = useQuery(`repoEncData-${getBoundsString(props.bounds)}-${props.search}}`, () =>
        fetch(`${config.api_url}/enc/get_by_area_bounds?bounds=${getBoundsString(props.bounds)}&search=${props.search}`).then((res) => res.json())
    );

    if (error_enc || error_enc) return <>'An error has occurred: ' + error</>;

    if (loading_enc || !data_enc) return <CustomSpinner message="Loading ENC-cells" />;

    return (
        <SettingsContext.Consumer>
            {({ settings, setSettings }) => (
                <>
                    {data_enc.map((enc: EncCell) => {
                        return (
                            <>
                                {enc.cell_title.toLocaleLowerCase().search(props.search.toLocaleLowerCase()) !== -1 ? (
                                    <Rectangle
                                        bounds={[
                                            [enc.location.coordinates[0][0][0], enc.location.coordinates[0][0][1]],
                                            [enc.location.coordinates[0][2][0], enc.location.coordinates[0][2][1]],
                                        ]}
                                        pathOptions={{ color: hashStringToColor(enc.cell_title) }}
                                    >
                                        <Popup>
                                            <h3>{enc.cell_title}</h3>
                                            <p>{enc.cell_name}</p>
                                            <label>Area</label>
                                            <p className="mt-0">{enc.area} km²</p>
                                            <h5>Actions</h5>
                                            {settings.shipTypesSelected.length < make_options(config.ship_types).length ? (
                                                <a
                                                    onClick={() => {
                                                        setSettings({ ...settings, shipTypesSelected: make_options(config.ship_types) });
                                                    }}
                                                >
                                                    Choose all
                                                </a>
                                            ) : (
                                                ""
                                            )}
                                            <CustomMultiSelect
                                                options={make_options(config.ship_types)}
                                                value={settings.shipTypesSelected}
                                                setValue={(values) => {
                                                    setSettings({ ...settings, shipTypesSelected: values });
                                                }}
                                            />
                                            <Row className="mt-2">
                                                <Col md={6}>
                                                    <Button
                                                        className="mb-2 w-100"
                                                        onClick={() => {
                                                            setSettings({ ...settings, encIdForTrack: enc.cell_id, showEnc: false });
                                                        }}
                                                        color="primary"
                                                        disabled={settings.shipTypesSelected.length == 0}
                                                    >
                                                        Show tracks
                                                    </Button>
                                                </Col>
                                                <Col md={6}>
                                                    <Button
                                                        className="mb-2 w-100"
                                                        color="primary"
                                                        disabled={settings.shipTypesSelected.length == 0}
                                                        onClick={() => {
                                                            setSettings({ ...settings, encIdForSimpleHeatMap: enc.cell_id, showEnc: false });
                                                        }}
                                                    >
                                                        Simple heatmap
                                                    </Button>
                                                </Col>
                                                <Col md={6}>
                                                    <Button
                                                        className="mb-2 w-100"
                                                        color="primary"
                                                        disabled={settings.shipTypesSelected.length == 0}
                                                        onClick={() => {
                                                            setSettings({ ...settings, encIdForTraficDensityHeatMap: enc.cell_id, showEnc: false });
                                                        }}
                                                    >
                                                        Trafic density heatmap
                                                    </Button>
                                                </Col>
                                            </Row>
                                        </Popup>
                                    </Rectangle>
                                ) : (
                                    ""
                                )}
                            </>
                        );
                    })}
                </>
            )}
        </SettingsContext.Consumer>
    );
};
