import * as React from 'react';
import { Popup, Rectangle } from 'react-leaflet';
import { useQuery } from 'react-query';
import { Button, Spinner } from 'reactstrap';
import { hashStringToColor } from '../../helpers/hash_strings';
import { EncCell } from '../../models/enc_cells';

interface Props {
    limit: number,
    offset: number,
    search: string,
}

export const MapEncCells = (props: Props) => {

    const decode_polygon_to_limits = (data: EncCell[]): EncCell[] => {
        // iterate every location in data and write new limit fields
        data.forEach(enc_cell => {
            console.log("point", enc_cell)
            enc_cell.westLimit = enc_cell.location.coordinates[0][0][0]
            enc_cell.northLimit = enc_cell.location.coordinates[0][0][1]
            enc_cell.eastLimit = enc_cell.location.coordinates[0][2][0]
            enc_cell.southLimit = enc_cell.location.coordinates[0][2][1]
        });

        return data;
    }

    const { isLoading: loading_enc, error: error_enc, data: data_enc } = useQuery(`repoEncData-${props.limit}-${props.offset}`, () =>
        fetch(`http://localhost:5000/get_enc_cells?limit=${props.limit}&offset=${props.offset}`).then(res =>
            res.json()
        ).then(encs =>
            decode_polygon_to_limits(encs)
        ));

    if (error_enc || error_enc) return <>'An error has occurred: ' + error</>


    if (loading_enc || !data_enc) return <Spinner />


    return (<>
        {data_enc.map((enc: EncCell) => {

            return (<>
                {
                    enc.cell_title.toLocaleLowerCase().search(props.search.toLocaleLowerCase()) !== -1 ? <Rectangle bounds={[[enc.northLimit, enc.westLimit], [enc.southLimit, enc.eastLimit]]} pathOptions={{ color: hashStringToColor(enc.cell_title) }}>
                        <Popup>
                            <h3>
                                {enc.cell_title}
                            </h3>
                            <p>
                                {enc.cell_name}
                            </p>
                            <Button>Show tracks in cell</Button>
                        </Popup>
                    </Rectangle> : ""
                }</>

            )
        })}</>);
}