import base64
import datetime
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import pathlib

from dash.dependencies import Input, Output, State

dir_path = pathlib.Path().absolute()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Giving positional col. names
colnames = ['Date', 'Class', 'MMSI', 'lat', 'lon', 'NavStatus', 'ROT', 'SOG', 'COG', 'Heading', 'IMO', 'Callsign', 'Name', 'ShipType', 'CargoType', 'Width', 'Length', 'TypeOfPosFixingDevice', 'Draught', 'Destination', 'ETA', 'DataSourceType', 'SizeA', 'SizeB', 'SizeC', 'SizeD'] # giving our AIS data some col. names

# Loading data in a Pandas data frame using data using read_csv and passing in col. names
ais_df = pd.read_csv("10k_aisdk_20210209.csv", header=None, names=colnames)

# Dash components section
app.layout = html.Div([
    html.H2("P6 AIS Data", style={'text-align': 'center'}),
    html.H3("Using first 10k rows of dataset aisdk_20210209", style={'text-align': 'center'}),

    # Graph
    html.H3("Graph Testing"),
    dcc.Dropdown(id="graph_input",
                 options=[
                     {"label": "ship data for 09/02/2021 01:16:47", "value": "timestamp"},
                     {"label": "ship data for one ship", "value": "one_ship"},
                     ],
                 multi=False,
                 value="timestamp",
                 style={'width': "40%"}
                 ),
    html.Div(id='output-graph'),
    html.Br(),
    dcc.Graph(id='my_ais_data', figure={}),

    # Pie Chart
    html.H3("Pie Chart Testing"),
    dcc.Dropdown(id="piechart_input",
                 options=[
                     {"label": "ship types", "value": "ShipType"},
                     {"label": "cargo types", "value": "CargoType"},
                    {"label": "class types", "value": "Class"},
                     ],
                 multi=False,
                 value="ShipType",
                 style={'width': "40%"}
                 ),

    html.Div(id='output-chart'),
    html.Br(),
    dcc.Graph(id='ais_ship_types', figure={}),

    # Upload data
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

# Callback method for uploading
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('my_ais_data', 'figure'), Input('graph_input', 'value'))
def show_graph(graph_input):
    print(graph_input)

    # Showing type of graph based on input
    if(graph_input == "timestamp"):
        updated_ais_data = ais_df.loc[ais_df['Date'] == "09/02/2021 01:16:47"]
    elif(graph_input == "one_ship"):
        updated_ais_data = ais_df.loc[ais_df['Name'] == "NKT VICTORIA"]
    else:
        updated_ais_data = ais_df

    fig = px.scatter_mapbox(updated_ais_data, lat="lat", lon="lon", hover_name="Name", hover_data=['Date', 'Class', 'MMSI', 'NavStatus', 'ROT', 'SOG', 'COG', 'Heading', 'IMO', 'Callsign', 'Name', 'ShipType'],
                            color_discrete_sequence=["red"], zoom=3, height=300)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Testing with piechart for now
@app.callback(Output('ais_ship_types', 'figure'), Input('piechart_input', 'value'))
def show_piechart(piechart_input):
    # Showing type of piechart based on input
    # TODO Implement

    updated_ais_data = ais_df # saving it again in case we messing with it
    piechart = px.pie(updated_ais_data, names=piechart_input, title='Ship types')
    return piechart


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=4000, debug=True)
