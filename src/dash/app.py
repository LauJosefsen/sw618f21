import json

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from dash import dash
from dash.dependencies import Input, Output, State

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

df = px.data.tips()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Giving col. names
colnames = [
    "Date",
    "Class",
    "MMSI",
    "lat",
    "lon",
    "NavStatus",
    "ROT",
    "SOG",
    "COG",
    "Heading",
    "IMO",
    "Callsign",
    "Name",
    "ShipType",
    "CargoType",
    "Width",
    "Length",
    "TypeOfPosFixingDevice",
    "Draught",
    "Destination",
    "ETA",
    "DataSourceType",
    "SizeA",
    "SizeB",
    "SizeC",
    "SizeD",
]

# Loading data in a Pandas data frame using data using read_csv and passing in col. names
ais_df = pd.read_csv("10k_aisdk_20210209.csv", header=None, names=colnames)

# Dash components section
app.layout = html.Div(
    [
        html.H2("P6 AIS Data", style={"text-align": "center"}),

        html.Div([
            # Get data from API
            html.Button('Get data', id='get_data_btn'),
            html.Div(id="output_data_api"),

            # Input to decide how much input to load
            html.P('Limit'),
            dcc.Input(id="input_limit", type="number", value=100, placeholder="", debounce=True),
            html.P('Offset'),
            dcc.Input(id="input_offset", type="number", value=10, placeholder="", debounce=True),
        ]),

        # Display data from API in graph
        html.Div(id="output-line-graph"),
        html.Br(),
        dcc.Graph(id="line_graph", figure={}),

        # Graph
        html.H3("Local data testing below"),
        dcc.Dropdown(
            id="graph_input",
            options=[
                {"label": "Ship data for 09/02/2021 01:16:47", "value": "timestamp"},
                {"label": "Ship data for one ship", "value": "one_ship"},
            ],
            multi=False,
            value="timestamp",
            style={"width": "40%"},
        ),
        html.Div(id="output-graph"),
        html.Br(),
        dcc.Graph(id="my_ais_data", figure={}),

        # Pie Chart
        html.H3("Pie Chart Testing"),
        dcc.Dropdown(
            id="piechart_input",
            options=[
                {"label": "Ship types", "value": "ShipType"},
                {"label": "Cargo types", "value": "CargoType"},
                {"label": "Class types", "value": "Class"},
            ],
            multi=False,
            value="ShipType",
            style={"width": "40%"},
            searchable=False,
        ),
        html.Div(id="output-chart"),
        html.Br(),
        dcc.Graph(id="ais_ship_types", figure={}),

        # Histogram
        html.H3("Histogram Testing"),
        dcc.Dropdown(
            id="histogram_input",
            options=[
                {"label": "Cargo Type", "value": "CargoType"},
                {"label": "COG", "value": "COG"},
                {"label": "Class", "value": "Class"},
                {"label": "Data Source Type", "value": "DataSourceType"},
                {"label": "Date", "value": "Date"},
                {"label": "Destination", "value": "Destination"},
                {"label": "Draught", "value": "Draught"},
                {"label": "ETA", "value": "ETA"},
                {"label": "IMO", "value": "IMO"},
                {"label": "Length", "value": "Length"},
                {"label": "NavStatus", "value": "NavStatus"},
                {"label": "ROT", "value": "ROT"},
                {"label": "SOG", "value": "SOG"},
                {"label": "Ship types", "value": "ShipType"},
                {"label": "Width", "value": "Width"},
            ],
            multi=False,
            value="ShipType",
            style={"width": "40%"},
            clearable=False,
        ),
        dcc.Graph(id="histogram", figure={}),
        # sliders for histogram
        dcc.RangeSlider(
            id="histogram_slider",
            marks={
                i: "{}".format(i)
                for i in {1, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500}
            },
            min=0,
            max=500,
            step=1,
            value=[1, 25],
        ),
    ]
)

@app.callback(Output("my_ais_data", "figure"), Input("graph_input", "value"))
def show_graph(graph_input):
    print(graph_input)

    # Showing type of graph based on input
    if graph_input == "timestamp":
        updated_ais_data = ais_df.loc[ais_df["Date"] == "09/02/2021 01:16:47"]
    elif graph_input == "one_ship":
        updated_ais_data = ais_df.loc[ais_df["Name"] == "NKT VICTORIA"]
    else:
        updated_ais_data = ais_df

    fig = px.scatter_mapbox(
        updated_ais_data,
        lat="lat",
        lon="lon",
        hover_name="Name",
        hover_data=[
            "Date",
            "Class",
            "MMSI",
            "NavStatus",
            "ROT",
            "SOG",
            "COG",
            "Heading",
            "IMO",
            "Callsign",
            "Name",
            "ShipType",
        ],
        color_discrete_sequence=["red"],
        zoom=3,
        height=600,
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


# Piechart callback
@app.callback(Output("ais_ship_types", "figure"), Input("piechart_input", "value"))
def show_piechart(piechart_input):
    # Showing type of piechart based on input
    updated_ais_data = ais_df  # saving it again in case we messing with it
    piechart = px.pie(updated_ais_data, names=piechart_input, title="Ship types")
    return piechart


@app.callback(
    Output("histogram", "figure"),
    [Input("histogram_input", "value"), Input("histogram_slider", "value")],
)
def show_histogram(histogram_input, histogram_slider):
    # Showing type of histogram based on input
    histogram_data = ais_df[
        histogram_input
    ]  # saving it again in case we messing with it
    histogram = px.histogram(
        histogram_data, nbins=30, range_x=[histogram_slider[0], histogram_slider[1]]
    )
    return histogram


# Callback for retrieving data from the button
@app.callback(
    Output("line_graph", "figure"),
    [Input('get_data_btn', 'n_clicks'),
     Input('input_limit', 'value'),
     Input('input_offset', 'value')],
)
def get_data(n_clicks, input_limit, input_offset):
    api_json = get_json_api(input_limit, input_offset)

    lats = []
    lons = []
    names = []

    for course in api_json:
        mmsi = course['mmsi']
        for coord in course['coordinates']:
            lats = np.append(lats, coord[1])
            lons = np.append(lons, coord[0])
            names = np.append(names, mmsi)
        lats = np.append(lats, None)
        lons = np.append(lons, None)
        names = np.append(names, None)

    # print(lats)
    # print(lons)
    # print(names)

    fig = px.line_mapbox(lat=lats, lon=lons, hover_name=names,
                         mapbox_style="stamen-terrain", zoom=6)
    return fig



def get_json_api(limit, offset=0):
    payload = {'limit': limit, 'offset':offset}
    response = requests.get(f'http://api:5000/routes', params=payload)
    content = response.content
    y = json.loads(content)

    #print(json.dumps(y))
    for course in y:
        print(course['mmsi'])

    return y

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=4000, debug=True)
