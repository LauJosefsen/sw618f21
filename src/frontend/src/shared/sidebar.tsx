import * as React from 'react';
import { Component } from 'react';
import Sidebar from "react-sidebar";
import { Button, Input, Label } from 'reactstrap';
import { SettingsContext } from '../providers/settings_provider';

export const CustomSidebar = () => {

    const [sidebarOpen, setSidebarOpen] = React.useState<boolean>(false)

    return (

        <Sidebar
            sidebar={
                <SettingsContext.Consumer>
                    {({ settings, setSettings }) => (
                        <>
                            <p>Sidebar content</p>
                            <Button onClick={() => { setSettings({ ...settings, showEnc: !settings.showEnc }) }}>{settings.showEnc ? "Hide ENC" : "Show ENC"}</Button>
                            <Label>ENC</Label>
                            <Input type="number" value={settings.encLimit} onChange={(e) => { setSettings({ ...settings, encLimit: parseInt(e.currentTarget.value) }) }} />
                            <Input type="text" value={settings.encSearch} onChange={(e) => { setSettings({ ...settings, encSearch: e.currentTarget.value }) }} />
                            <Button className="sidebar-button" onClick={() => setSidebarOpen(false)}>Close sidebar</Button>
                            <h3>Tracks</h3>
                            <Label>Limit</Label>
                            <Input type="number" value={settings.trackLimit} onChange={(e) => { setSettings({ ...settings, trackLimit: parseInt(e.currentTarget.value) }) }} />
                            <Label>Offset</Label>
                            <Input type="number" value={settings.trackOffset} onChange={(e) => { setSettings({ ...settings, trackOffset: parseInt(e.currentTarget.value) }) }} />
                            <Label>Search</Label>
                            <Input type="text" value={settings.trackSearch} onChange={(e) => { setSettings({ ...settings, trackSearch: e.currentTarget.value }) }} />
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

}