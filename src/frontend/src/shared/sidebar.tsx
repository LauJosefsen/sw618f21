import * as React from "react";
import Sidebar from "react-sidebar";
import { Button, Input, Label } from "reactstrap";
import { settings, SettingsContext } from "../providers/settings_provider";
import "rc-slider/assets/index.css";

export const CustomSidebar = () => {
    const [sidebarOpen, setSidebarOpen] = React.useState<boolean>(false);

    const toggleEncBoundsKey = (settings: settings, key: string): settings => {
        settings.encBounds[key][0] = !settings.encBounds[key][0];
        return { ...settings };
    };

    return (
        <Sidebar
            sidebar={
                <SettingsContext.Consumer>
                    {({ settings, setSettings }) => (
                        <>
                            <p>Sidebar content</p>

                            <h3>ENC</h3>
                            <Button
                                onClick={() => {
                                    setSettings({ ...settings, showEnc: !settings.showEnc });
                                }}
                            >
                                {settings.showEnc ? "Hide ENC" : "Show ENC"}
                            </Button>
                            <br />
                            {!settings.showEnc ? (
                                ""
                            ) : (
                                <>
                                    <Label>Sizes shown</Label>
                                    <p className="ml-5">
                                        {Object.entries(settings.encBounds).map(([key, val]) => {
                                            return (
                                                <>
                                                    <Input
                                                        id={`${key}-enc`}
                                                        type="checkbox"
                                                        checked={val[0]}
                                                        onChange={() => {
                                                            setSettings(toggleEncBoundsKey(settings, key));
                                                        }}
                                                    />
                                                    <Label for={`${key}-enc`}>
                                                        {key} ENC ({val[1]}-{val[2]} km²)
                                                    </Label>
                                                    <br />
                                                </>
                                            );
                                        })}
                                    </p>
                                    <Label>Search</Label>
                                    <Input
                                        type="text"
                                        value={settings.encSearch}
                                        onChange={(e) => {
                                            setSettings({ ...settings, encSearch: e.currentTarget.value });
                                        }}
                                    />
                                </>
                            )}

                            <h3>Depth map</h3>
                            <Button
                                onClick={() => {
                                    setSettings({ ...settings, showDepthMap: !settings.showDepthMap });
                                }}
                            >
                                {settings.showDepthMap ? "Hide" : "Show"}
                            </Button>

                            <Button className="sidebar-button" onClick={() => setSidebarOpen(false)}>
                                Close sidebar
                            </Button>
                        </>
                    )}
                </SettingsContext.Consumer>
            }
            open={sidebarOpen}
            onSetOpen={setSidebarOpen}
            styles={{ sidebar: { background: "#282c34", color: "white", padding: "2em", width: "25vw", zIndex: "2000" } }}
        >
            <Button className="sidebar-button" onClick={() => setSidebarOpen(true)}>
                Open sidebar
            </Button>
        </Sidebar>
    );
};
