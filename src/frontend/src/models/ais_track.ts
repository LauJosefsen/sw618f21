export interface AisTrack{
    id: number,
    mmsi: number,
    timestamp_begin: Date,
    timestamp_end: Date,
    coordinates: [number, number][]
}
