import * as React from 'react';
import L from 'leaflet'
import 'leaflet.heat';
import {useMap} from "react-leaflet";
import {useEffect} from "react";

interface Props {
    data: [number, number, number][]
}

export const HeatMap = (props: Props) => {

    const map = useMap()
    useEffect(() => {
        const points = props.data ? props.data : [];


        L.heatLayer(points, { radius: 10 }).addTo(map);
    },[])



    return (
        <>

        </>

    )
}