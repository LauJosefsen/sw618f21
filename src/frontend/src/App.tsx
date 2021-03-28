import './App.css';
import * as L from 'leaflet';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import { CustomSidebar } from './shared/sidebar';
import { MapEncCells } from './shared/map/enc_cells';
import { MapTrack } from './shared/map/track';
import { settings, SettingsContext, settings_with_setter } from './providers/settings_provider';
import { useEffect, useState } from 'react';

function App() {

    const [local_settings, setSettings] = useState<settings>(
        {
            showEnc: true,
            encOffset: 0,
            encLimit: 5,
            showTrack: true,
            trackOffset: 0,
            trackLimit: 0,
            search_filters: []

        }
    )


    return (
        <>

            <SettingsContext.Provider value={{ settings: local_settings, setSettings: setSettings }} >
                <CustomSidebar />
                <header className="App-header">
                    <MapContainer center={[56, 10]} zoom={7} scrollWheelZoom={true}>
                        <TileLayer
                            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <SettingsContext.Consumer>
                            {({ settings }) => (
                                <>
                                    {settings.showEnc ? <MapEncCells limit={settings.encLimit} offset={settings.encOffset} /> : ""}
                                </>
                            )}
                        </SettingsContext.Consumer>
                        <MapTrack />
                    </MapContainer>
                </header>
            </SettingsContext.Provider>
        </>
    );
}

export default App;
