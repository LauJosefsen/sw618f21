import { Popup, Rectangle } from "react-leaflet";
import { useQuery } from "react-query";
import { Button } from "reactstrap";
import { hashStringToColor } from "../../helpers/hash_strings";
import { EncCell } from "../../models/enc_cells";
import { SettingsContext } from "../../providers/settings_provider";
import { CustomSpinner } from "../custom_spinner";
import { config } from '../../helpers/constants'

interface Props {
    bounds: { [key: string]: [boolean, number, number] };
    search: string;
}

export const MapEncCells = (props: Props) => {
    const decode_polygon_to_limits = (data: EncCell[]): EncCell[] => {
        // iterate every location in data and write new limit fields
        data.forEach((enc_cell) => {
            enc_cell.westLimit = enc_cell.location.coordinates[0][0][0];
            enc_cell.northLimit = enc_cell.location.coordinates[0][0][1];
            enc_cell.eastLimit = enc_cell.location.coordinates[0][2][0];
            enc_cell.southLimit = enc_cell.location.coordinates[0][2][1];
        });

        return data;
    };

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
        fetch(`${config.api_url}/enc/get_by_area_bounds?bounds=${getBoundsString(props.bounds)}&search=${props.search}`)
            .then((res) => res.json())
            .then((encs) => decode_polygon_to_limits(encs))
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
                                            [enc.northLimit, enc.westLimit],
                                            [enc.southLimit, enc.eastLimit],
                                        ]}
                                        pathOptions={{ color: hashStringToColor(enc.cell_title) }}
                                    >
                                        <Popup>
                                            <h3>{enc.cell_title}</h3>
                                            <p>{enc.cell_name}</p>
                                            <label>Area</label>
                                            <p className="mt-0">{enc.area} km²</p>
                                            <label>Tracks</label>
                                            <div>
                                                <Button onClick={() => { setSettings({...settings, encIdForTrack: enc.cell_id, showEnc: false})}} color="primary">Show tracks in cell</Button>
                                            </div>
                                            <label>Heatmap</label>
                                            <div>
                                                <Button
                                                    onClick={() => {
                                                        setSettings({ ...settings, encIdForHeatMap: enc.cell_id, showEnc: false });
                                                    }}
                                                >
                                                    Show heatmap in enc_cell
                                            </Button>
                                            </div>

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
