import "./App.css";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer } from "react-leaflet";

import { CustomSidebar } from "./shared/sidebar";
import { MapEncCells } from "./shared/map/enc_cells";
import { settings, SettingsContext } from "./providers/settings_provider";
import React, { useState } from "react";
import { SimpleHeatMap } from "./shared/map/simple_heatmap";
import { MapTrack } from "./shared/map/track";
import { TraficDensityHeatMap } from "./shared/map/trafic_density_heatmap";
import { make_options } from "./helpers/make_options";
import { config } from "./helpers/constants";

function App() {
    const [local_settings, setSettings] = useState<settings>({
        shipTypesSelected: make_options(config.ship_types),
        encSearch: "",
        showEnc: true,
        encBounds: { ExtraSmall: [true, 0, 100], Small: [true, 100, 3000], Medium: [true, 3000, 50000], Large: [true, 50000, 10000000] },
        encIdForTrack: undefined,
        encIdForHeatMap: undefined,
    });

    return (
        <>
            <SettingsContext.Provider value={{ settings: local_settings, setSettings: setSettings }}>
                <CustomSidebar />
                <header className="App-header">
                    <MapContainer center={[56, 10]} zoom={7} scrollWheelZoom>
                        <TileLayer attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                        {/* <TileLayer
                            url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
                            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                        /> */}
                        <SettingsContext.Consumer>
                            {({ settings }) => (
                                <>
                                    {settings.showEnc ? <MapEncCells bounds={settings.encBounds} search={settings.encSearch} /> : ""}
                                    {settings.encIdForTrack ? <MapTrack enc_cell_id={settings.encIdForTrack} ship_types={settings.shipTypesSelected.map((ship) => ship.value)} /> : ""}

                                    {/* {settings.encIdForHeatMap ? <TraficDensityHeatMap enc_cell_id={settings.encIdForHeatMap} ship_types={settings.shipTypesSelected.map((ship) => ship.value)} /> : ""} */}
                                    {settings.encIdForHeatMap ? <SimpleHeatMap enc_cell_id={settings.encIdForHeatMap} ship_types={settings.shipTypesSelected.map((ship) => ship.value)} /> : ""}
                                </>
                            )}
                        </SettingsContext.Consumer>
                        {/* <MapHeatMapGrid/> */}
                        {/* <MapPoints /> */}
                    </MapContainer>
                </header>
            </SettingsContext.Provider>
        </>
    );
}

export default App;
