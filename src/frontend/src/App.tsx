import './App.css'
import 'leaflet/dist/leaflet.css'
import { MapContainer, TileLayer } from 'react-leaflet'

import { CustomSidebar } from './shared/sidebar'
import { MapEncCells } from './shared/map/enc_cells'
import { MapTrack } from './shared/map/track'
import { MapPoints } from './shared/map/points'
import { settings, SettingsContext, settings_with_setter } from './providers/settings_provider'
import React, { useEffect, useState } from 'react'
import { HeatMap } from './heatmap'
import { MapHeatMapGrid } from './shared/map/heatmap_grid'

function App () {
  const [local_settings, setSettings] = useState < settings > (
    {
      encSearch: '',
      showEnc: false,
      encOffset: 0,
      encLimit: 5,
      showTrack: true,
      trackOffset: 0,
      trackLimit: 5,
      trackSearch: ''

    }
  )

  return (
    <>

      <SettingsContext.Provider value={{ settings: local_settings, setSettings: setSettings }}>
        <CustomSidebar />
        <header className='App-header'>
          <MapContainer center={[56, 10]} zoom={7} scrollWheelZoom>
            <TileLayer
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            />
            {/* <TileLayer
                            url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
                            attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                        /> */}
            <SettingsContext.Consumer>
              {({ settings }) => (
                <>
                  {/* {settings.showEnc ? <MapEncCells limit={settings.encLimit} offset={settings.encOffset} search={settings.encSearch} /> : ''}
                  {settings.showTrack ? <MapTrack limit={settings.trackLimit} offset={settings.trackOffset} search={settings.trackSearch} /> : ''} */}
                </>
              )}

            </SettingsContext.Consumer>
            <MapHeatMapGrid/>
            {/* <MapPoints /> */}
            <HeatMap data={[[57, 11, 100]]} />
          </MapContainer>
        </header>
      </SettingsContext.Provider>
    </>
  )
}

export default App
