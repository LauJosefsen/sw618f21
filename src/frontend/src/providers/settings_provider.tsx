import React from "react"

export interface settings {

    // ENC:
    showEnc: boolean
    encOffset: number;
    encLimit: number;
    encSearch: string;

    // TRACKS:
    showTrack: boolean
    trackOffset: number;
    trackLimit: number;
    search_filters: any;
}

export interface settings_with_setter {
    // Everything that is saved and may be needed in multiple components:
    setSettings: (arg0: settings) => void
    settings: settings


}
export const SettingsContext = React.createContext<settings_with_setter>({
    setSettings: () => { },
    // These values do not really matter, as they are always overwritten in App.
    settings: {
        encSearch: "",
        showEnc: true,
        encOffset: 0,
        encLimit: 5,
        showTrack: true,
        trackOffset: 0,
        trackLimit: 0,
        search_filters: []
    }

})