import React from "react";

export interface settings {
    // ENC:
    showEnc: boolean;
    encBounds: { [key: string]: [boolean, number, number] };
    encSearch: string;

    // TRACKS:
    encIdForTrack: number | undefined;

    // HEATMAP
    encIdForHeatMap: number | undefined;
}

export interface settings_with_setter {
    // Everything that is saved and may be needed in multiple components:
    setSettings: (arg0: settings) => void;
    settings: settings;
}
export const SettingsContext = React.createContext<settings_with_setter>({
    setSettings: () => {},
    // These values do not really matter, as they are always overwritten in App.
    settings: {
        encSearch: "",
        showEnc: true,
        encBounds: { small: [true, 0, 1000000], medium: [true, 1000000, 10000000], large: [true, 10000000, 10000000000000] },
        encIdForTrack: undefined,
        encIdForHeatMap: undefined,
    },
});
