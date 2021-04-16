import { MapEncCells } from "../shared/map/enc_cells";
import { GeoJsonLocation } from "./location";

export interface EncCell {
    cell_id: number;
    cell_name: string;
    cell_title: string;
    area: number;
    location: GeoJsonLocation;
    southLimit: number;
    westLimit: number;
    northLimit: number;
    eastLimit: number;
}
