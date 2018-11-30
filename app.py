import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
import plotly
import plotly.graph_objs as go
import numpy as np
import urllib.parse
import requests
import pandas as pd
import plotly.figure_factory as ff
from scipy import stats
from scipy.stats import genextreme
import math as m

## Load CSV data

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]

custom_map_style = "mapbox://styles/mapbox/light-v9"

app = dash.Dash(__name__,
    external_stylesheets=external_css
)

turbine_locations = pd.read_csv('data/turbine_locations.csv')
mapbox_access_token = 'pk.eyJ1IjoiY2JvZGVpIiwiYSI6ImNqbzY3eG4wejBlN3UzcXBiNTk1a3N4NWsifQ.rAUKKJtNfW5Mw2GX8Tdoag'
token = '0939c8c78a5a460e8685922d985d500f' # API token
output = 'json'                            # Output format

app.layout = html.Div([
    html.Div([
        html.H2('Wind Turbine Dash'),
    ], className='banner'),
    dcc.Dropdown(
        id = 'dropdown',
        options = [
            {'label': i, 'value': i} for i in turbine_locations.turbine_id
        ]
    ),
    html.Div([
        html.Div([
            html.H3('Turbine Locations')
        ], className='Title'),
        html.Div([
            dcc.Graph(id='map', figure={
                'data': [{
                    'lat': turbine_locations.latitude,
                    'lon': turbine_locations.longitude,
                    'mode': 'markers+text',
                    'marker': {
                        'size': 15,
                        'symbol': 'circle',
                        'color': '#42c4f7',
                    },
                    'text': turbine_locations.turbine_id,
                    #'textposition': 'top center',
                    'hoverinfo': 'text',
                    'textfont': {
                        'size': 1,
                        'color': '#42c4f7',
                    },
                    'type': 'scattermapbox',
                }],
                'layout': {
                    'autosize': True,
                    'clickmode': 'event',
                    'hovermode': 'closest',
                    #'dragmode': 'select',
                    'mapbox': {
                        'accesstoken': mapbox_access_token,
                        'center': {
                            'lat': 42.66,
                            'lon': -76.61,
                        },
                        'style': custom_map_style,
                        'pitch': 0,
                        'zoom': 7,
                    },
                    'margin': {'l': 50, 'r': 50, 'b': 0, 't': 0}
                }
            }),
        ]),
    ], className='row wind-speed-row'),
    html.Div([
        html.Div([
            html.Div([
                html.H3('WIND SPEED HISTOGRAM')
            ], className='Title'),
            dcc.Graph(id='histogram'),
        ], className='seven columns wind-histogram'),
        html.Div([
            html.Div([
                html.H3('Turbine Status')
            ], className='Title'),
            dt.DataTable(
                id ='table',
                columns=[
                    {'name': 'Status', 'id': 'Status'},
                    {'name': 'Power (watts)', 'id': 'Power (watts)'},
                    {'name': 'Energy Today (kWh)', 'id': 'Energy Today (kWh)'},
                    {'name': 'Energy 7 days (kWh)', 'id': 'Energy 7 days (kWh)'},
                    {'name': 'Energy 30 days (kWh)', 'id': 'Energy 30 days (kWh)'},
                    {'name': 'AC Voltage (VAC)', 'id': 'AC Voltage (VAC)'},
                    {'name': 'DC Voltage (VDC)', 'id': 'DC Voltage (VDC)'},
                    {'name': 'DC Current (amps)', 'id': 'DC Current (amps)'}
                ],
                style_cell_conditional=[
                    {'if': {'column_id': 'Status'},
                     'width': '130px'},
                ],
                data = [],
                editable=True
            )
        ], className='wind-polar ')
    ], className='row wind-histo-polar'),
    html.Div([
        html.P('\
            Status  .fm;km;ekfmk em;fm;e mfl;melmfmen ngnknkrngkr nkgnke;ms\
            testfmkfkejfkjkefkekfkekfefjeieoifjiejfoiejfijefjo\
            yaykfekfmkengnlrjkjgkrj jkjgkjrkgj; rjjkgjr kj;grk kjg\
            yepsss lkgrkljgl kjgk jlkrjsjgk jkjgkjr jgkrslgjj jg', 
            id='turbine-status'
        ),
    ], className='seven columns wind-histogram')

], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})

@app.callback(
    Output('histogram', 'figure'),
    [Input('map', 'clickData'),
    Input('dropdown','value')]
)
def closest_station(value1,value2):
    if value1 != value2:
        s = turbine_locations[turbine_locations['turbine_id'] == value2]
    else:
        s = turbine_locations[turbine_locations['turbine_id'] == value1['points'][0]['text']]

    latitude = str(s.iloc[0]['latitude'])
    longitude = str(s.iloc[0]['longitude'])

    #########################################################
    ## Find closest weather station to turbine coordinates ##
    #########################################################
    radius = '20'

    # Station metadata API URL
    metadata_api = 'https://api.synopticlabs.org/v2/stations/metadata?&'

    # URL to be sent to API
    url = metadata_api + urllib.parse.urlencode({'token': token,
                                                 'output': output,
                                                 'radius': latitude+','+longitude+','+radius,
                                                 'limit': '10',
                                                 'vars': 'wind_speed,wind_direction'
                                                 })

    # API GET request
    json_data = requests.get(url).json()
    json_number_of_stations = json_data['SUMMARY']['NUMBER_OF_OBJECTS']

    # Intialize lists
    station_id = []
    station_distance = []
    station_index = []

    for i in range(0, int(json_number_of_stations)):
        json_period_start = json_data['STATION'][i]['PERIOD_OF_RECORD']['start']
        json_period_end = json_data['STATION'][i]['PERIOD_OF_RECORD']['end']
        json_station_id = json_data['STATION'][i]['STID']
        json_station_distance = json_data['STATION'][i]['DISTANCE']
        if (int(json_period_end[:-16]) - int(json_period_start[:-16])) >= 9:
            station_distance.insert(i,json_station_distance)
            station_id.insert(i,json_station_id)
            station_index.insert(i,i)
    if not station_distance:
        print('No weather stations within ' + radius + ' miles have 10 years of wind speed data, try increasing range.')
        quit()

    min_station_distance = min(station_distance)
    min_station_distance_idx = station_distance.index(min_station_distance)
    closest_station = station_id[min_station_distance_idx]
    df = pd.read_csv('data/'+closest_station+'.csv')

    trace0 = go.Histogram(
        x=df.wind_speed,
        histnorm='probability',
        nbinsx = 50,
        marker=dict(
            color='#42c4f7'
        ),
    ),
    layout = go.Layout(
        title='Wind Speed Frequency',
        xaxis=dict(
            title='Wind Speed'
        ),
        yaxis=dict(
            title='Frequency'
        ),
    )
    figure = go.Figure(trace0,layout)
    return figure

@app.callback(
    Output('dropdown', 'value'),
    [Input('map','clickData')]
)
def update_dropdown(clickData):
    value = clickData['points'][0]['text']
    return value

@app.callback(
    Output('table', 'data'),
    [Input('map','clickData'),
    Input('dropdown', 'value')]
)
def turbine_status(clickData, value):

    if clickData != value:
        turbine_id = value
    else:
        turbine_id = clickData['points'][0]['text']

    turbine_api_status = 'http://mybergey.aprsworld.com/data/jsonMyBergey.php?'
    url= turbine_api_status + urllib.parse.urlencode({
        'station_id': turbine_id,
        'statsHours': '24',
    })+'&_=1543523946153'

    json_data = requests.get(url).json()

    d = {'Status': json_data['inverter_systemStateText'],
        'Power (watts)': [json_data['inverter_output_power']],
        'Energy Today (kWh)': [json_data['inverter_energy_produced_today']],
        'Energy 7 days (kWh)': [json_data['inverter_energy_produced_last_7_days']],
        'Energy 30 days (kWh)': [json_data['inverter_energy_produced_last_30_days']],
        'AC Voltage (VAC)': [json_data['inverter_ac_voltage']],
        'DC Voltage (VDC)': [json_data['inverter_dc_voltage']],
        'DC Current (amps)': [json_data['inverter_dc_current']],
    }
    df = pd.DataFrame(data=d)

    return df.to_dict('rows')

if __name__ == '__main__':
    app.run_server(debug=True)