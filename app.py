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
import time
from closest_station import closest_station
from datetime import datetime
from station_status import station_status
from wind_gust import wind_gust
from turbine_history import turbine_history
from expected_power import expected_power
import os

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]

custom_map_style = "mapbox://styles/mapbox/light-v9"
turbine_locations = pd.read_csv('data/turbine_locations.csv')
mapbox_access_token = 'pk.eyJ1IjoiY2JvZGVpIiwiYSI6ImNqbzY3eG4wejBlN3UzcXBiNTk1a3N4NWsifQ.rAUKKJtNfW5Mw2GX8Tdoag'
token = '0939c8c78a5a460e8685922d985d500f' # API token
output = 'json'

app = dash.Dash(__name__,
    external_stylesheets=external_css
)
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')

app.layout = html.Div([
    html.Div([
        html.H2('Wind Turbine Dash'),
    ], className='banner'),
    html.Div([
        html.Div([
            html.H3('Selected Turbine')           
        ], className='Title'),
        html.Div([
            dcc.Dropdown(
                id = 'dropdown',
                options = [
                    {'label': i, 'value': i} for i in turbine_locations.turbine_id
                ]
            ),
        ])
    ], className='row wind-speed-row'),
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
                    'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
                }
            }),
        ]),
    ], className='row wind-speed-row'),
    html.Div([
        html.Div([
            html.Data([
                html.H3('Nearest Weather Station')
            ], className='Title'),
            dt.DataTable(
                id ='table2',
                #style_data={'whiteSpace': 'normal'},
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }],
                columns=[
                    {'name': 'Name', 'id': 'Name'},
                    {'name': 'Station ID', 'id': 'Station ID'},
                    {'name': 'Wind Speed (m/s)', 'id': 'Wind Speed'},
                    {'name': 'Wind Gust (m/s)', 'id': 'Wind Gust'},
                    {'name': 'Wind Direction', 'id': 'Wind Direction'},
                ],
                style_cell={
                    'whiteSpace': 'no-wrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                },
                editable=True
            ),
            dcc.Interval(
                id='interval-component2',
                interval=5*1000, # in milliseconds
                n_intervals=0
            ),
        ], className='wind-polar'),
        html.Div([
            html.Div([
                html.H3('Wind Speed Histogram (10 years)')
            ], className='Title'),
            dcc.Graph(id='histogram'),
        ], className='wind-polar'),
        html.Div([
            html.Div([
                html.H3('Wind Turbine Status')
            ], className='Title'),
            dt.DataTable(
                id ='table',
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }],
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
                style_cell={
                    'whiteSpace': 'no-wrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                },
                editable=True
            ),
            dcc.Interval(
                id='interval-component',
                interval=60*1000, # in milliseconds
                n_intervals=0
            ),
        ], className='wind-polar'),
        html.Div([
            html.Div([
                html.H3('Output Power (Watts) from the last 72 hours')
            ], className='Title'),
            dcc.Graph(id='history'),
            dcc.Interval(
                id='interval-component-3',
                interval=60*1000, # in milliseconds
                n_intervals=0
            ),
        ], className='wind-polar'),
        html.Div([
            html.Div([
                html.H3('Expected Power (Watts) from the last 72 hours')
            ], className='Title'),
            dcc.Graph(id='power'),
            dcc.Interval(
                id='interval-component-4',
                interval=60*1000, # in milliseconds
                n_intervals=0
            ),
        ], className='wind-polar'),
        html.Div([
            html.Div([
                html.H3('Wind Speed (m/s) from the last 72 hours')
            ], className='Title'),
            dcc.Graph(id='wind_history'),
            dcc.Interval(
                id='interval-component-5',
                interval=60*1000, # in milliseconds
                n_intervals=0
            ),
        ], className='wind-polar'),
        html.Div([
            html.A(html.Button('GitHub', className='three columns'),
            href='https://github.com/bodei/windapp'),
        ], className='wind-polar'),
    ], className='row wind-histo-polar'),
], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "1080",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})

@app.callback(
    Output('dropdown', 'value'),
    [Input('map','clickData')]
)
def update_dropdown(clickData):
    value = clickData['points'][0]['text']
    return value

@app.callback(
    Output('table2', 'data'),
    [Input('map','clickData'),
    Input('dropdown', 'value'),
    Input('interval-component', 'n_intervals')]
)
def station_status_update(clickData, value, n):
    if clickData != value:
        s = turbine_locations[turbine_locations['turbine_id'] == value]
    else:
        s = turbine_locations[turbine_locations['turbine_id'] == clickData['points'][0]['text']]

    latitude = str(s.iloc[0]['latitude'])
    longitude = str(s.iloc[0]['longitude'])

    station = closest_station(latitude,longitude)

    d = station_status(station)
    df = pd.DataFrame([d])
    return df.to_dict('rows')

@app.callback(
    Output('histogram', 'figure'),
    [Input('map', 'clickData'),
    Input('dropdown','value')]
)
def update_histogram(clickData,value):

    if clickData != value:
        s = turbine_locations[turbine_locations['turbine_id'] == value]
    else:
        s = turbine_locations[turbine_locations['turbine_id'] == clickData['points'][0]['text']]

    latitude = str(s.iloc[0]['latitude'])
    longitude = str(s.iloc[0]['longitude'])

    station = closest_station(latitude,longitude)

    df = pd.read_csv('data/'+station+'.csv')

    trace0 = go.Histogram(
        x=df.wind_speed,
        histnorm='probability',
        nbinsx = 50,
        marker=dict(
            color='#42c4f7'
        ),
    ),
    layout = go.Layout(
        xaxis=dict(
            title='Wind Speed (m/s)'
        ),
        yaxis=dict(
            title='Frequency'
        ),
    )
    figure = go.Figure(trace0,layout)
    return figure

@app.callback(
    Output('table', 'data'),
    [Input('map','clickData'),
    Input('dropdown', 'value'),
    Input('interval-component', 'n_intervals')]
)
def turbine_status(clickData, value, n):

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

@app.callback(
    Output('history','figure'),
    [Input('dropdown','value'),
    Input('map','clickData'),
    Input('interval-component-3', 'n_intervals')]
)
def history(value,clickData,n):
    if clickData != value:
        value = value
    else:
        value = clickData['points'][0]['text']

    df = turbine_history(value)

    trace0 = go.Scatter(
        x=df.time,
        y=df.output,
        line = dict(
            color = '#42c4f7',
        ),
        fill = 'tozeroy',
    ),
    layout = go.Layout(
        #type='date',
    )
    figure = go.Figure(trace0,layout)
    return figure

@app.callback(
    Output('power','figure'),
    [Input('dropdown','value'),
    Input('map','clickData'),
    Input('interval-component-4', 'n_intervals')]
)
def update_power(value,clickData,n):
    if clickData != value:
        s = turbine_locations[turbine_locations['turbine_id'] == value]
    else:
        s = turbine_locations[turbine_locations['turbine_id'] == clickData['points'][0]['text']]
    
    if clickData != value:
        value = value
    else:
        value = clickData['points'][0]['text']

    latitude = str(s.iloc[0]['latitude'])
    longitude = str(s.iloc[0]['longitude'])

    station = closest_station(latitude,longitude)
    df = expected_power(station)
    df2 = turbine_history(value)

    trace0 = go.Scattergl(
        x=df.time,
        y=df.power,
        name='Expected Power',
        line = dict(
            color = '#42c4f7',
        ),
        fill = 'tozeroy',
    )
    trace1 = go.Scatter(
        x=df2.time,
        y=df2.output,
        name='Actual Power',
        line = dict(
            color = 'red',
        ),
        fill = 'tozeroy',
        visible='legendonly',
    )
    layout = go.Layout(
        xaxis=dict(
           type='date',
        ),
    )
    data = [trace0, trace1]
    figure = go.Figure(data,layout)
    return figure

@app.callback(
    Output('wind_history','figure'),
    [Input('dropdown','value'),
    Input('map','clickData'),
    Input('interval-component-5', 'n_intervals')]
)
def wind_history(value,clickData,n):
    if clickData != value:
        s = turbine_locations[turbine_locations['turbine_id'] == value]
    else:
        s = turbine_locations[turbine_locations['turbine_id'] == clickData['points'][0]['text']]

    latitude = str(s.iloc[0]['latitude'])
    longitude = str(s.iloc[0]['longitude'])

    station = closest_station(latitude,longitude)
    windGust,windSpeed,date = wind_gust(station)

    trace0 = go.Scattergl(
        x=date,
        y=windGust,
        name='Wind Gust',
        line = dict(
            color = '#42c4f7',
        ),
        fill = 'tozeroy',
    )
    trace1 = go.Scattergl(
        x=date,
        y=windSpeed,
        name='Wind Speed',
        mode='lines',
        line = dict(
            color = '#05A8E6',
        ),
        fill = 'tozeroy',
    )
    layout = go.Layout(
        xaxis=dict(
           type='date',
        ),
        #legend=dict(orientation="h")
    )
    data = [trace0,trace1]
    figure = go.Figure(data,layout)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)