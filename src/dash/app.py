import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import plotly.express as px

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# 3 pillars
# dash components
# callbacks
#



# Loading data in a Pandas data frame
# Giving positional col. names
colnames = ['Date', 'Class', 'MMSI', 'lat', 'lon', 'NavStatus', 'ROT', 'SOG', 'COG', 'Heading', 'IMO', 'Callsign', 'Name', 'ShipType', 'CargoType', 'Width', 'Length', 'TypeOfPosFixingDevice', 'Draught', 'Destination', 'ETA', 'DataSourceType', 'SizeA', 'SizeB', 'SizeC', 'SizeD'] # giving our AIS data some col. names

# Loading data using read_csv and passing in col. names
ais_data = pd.read_csv("test_data/10k_aisdk_20210209.csv", header=None, names=colnames)

# Some test code to use the different data for the components, this can be copied in callback methods and sorted (probably makes more sense).
#ais_data = ais_data.loc[ais_data['Name'] == "NKT VICTORIA"]
ais_data = ais_data.loc[ais_data['Date'] == "09/02/2021 01:16:47"]
#ais_data = ais_data.loc[ais_data['Class'] == "Class B"]

# HTML section sort of with Dash components
app.layout = html.Div([
    html.H1("P6 AIS Data", style={'text-align': 'center'}),

    dcc.Dropdown(id="dummy_input",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),
    html.Div(id='output-graph'),
    html.Br(),
    dcc.Graph(id='my_ais_data', figure={}),

    dcc.Dropdown(id="dummy_input2",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    html.Div(id='output-chart'),
    html.Br(),
    dcc.Graph(id='ais_ship_types', figure={}),

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

# Some method for uploading data, ignore for now
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

# Callback method for showing graph. Might not need a callback, I think there are alternatives
# Using dummy_input for now because it is required in the callbacks
@app.callback(Output('my_ais_data', 'figure'), Input('dummy_input', 'value'))
def show_graph(dummy_input):
    print(dummy_input)
    # Plotly Express
    fig = px.scatter_mapbox(ais_data, lat="lat", lon="lon", hover_name="Name", hover_data=['Date', 'Class', 'MMSI', 'NavStatus', 'ROT', 'SOG', 'COG', 'Heading', 'IMO', 'Callsign', 'Name', 'ShipType'],
                            color_discrete_sequence=["red"], zoom=3, height=300)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Callback method for showing pie chart. Might not need a callback, I think there are alternatives
# Using dummy_input for now because it is required in the callbacks
@app.callback(Output('ais_ship_types', 'figure'), Input('dummy_input2', 'value'))
def show_graph(dummy_input2):
    # Plotly Express
    x_ais_data = ais_data # saving it again in case we messing with it
    fig = px.pie(x_ais_data, values='ShipType', names='Class', title='Ship types')
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)
