import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
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

app = dash.Dash()

turbine_locations = pd.read_csv('turbine_locations.csv')
mapbox_access_token = 'pk.eyJ1IjoiY2JvZGVpIiwiYSI6ImNqbzY3eG4wejBlN3UzcXBiNTk1a3N4NWsifQ.rAUKKJtNfW5Mw2GX8Tdoag'
token = '0939c8c78a5a460e8685922d985d500f' # API token
output = 'json'                            # Output format

app.layout = html.Div([
    html.H1('New York Wind Turbine Monitor'),
    dcc.Graph(id='map', figure={
        'data': [{
            'lat': turbine_locations.latitude,
            'lon': turbine_locations.longitude,
            'mode': 'markers+text',
            'marker': {
                    'size': 10,
                    'symbol': 'circle',
                    'color': '#3bb2d0',
            },
            'text': turbine_locations.turbine_id,
            'textposition': 'top center',
            'type': 'scattermapbox',
            #'selectedpoints': []
        }],
        'layout': {
            'autosize': True,
            'clickmode': 'select',
            'hovermode': 'closest',
            'dragmode': 'select',
            'mapbox': {
                'accesstoken': mapbox_access_token,
                'center': {
                    'lat': 42.66,
                    'lon': -76.61,
                },
                'pitch': 0,
                'zoom': 7,
            },
            'margin': {'l': 50, 'r': 50, 'b': 0, 't': 0}
        }
    }),
    #html.Div(id='station-text'),
    dcc.Graph(id='histogram'),
])

@app.callback(
    dash.dependencies.Output('histogram', 'figure'),
    [dash.dependencies.Input('map', 'clickData')])


def closest_station(clickData):
    s = turbine_locations[turbine_locations['turbine_id'] == clickData['points'][0]['text']]
    latitude = str(s.iloc[0]['latitude'])
    longitude = str(s.iloc[0]['longitude'])


    #########################################################
    ## Find closest weather station to turbine coordinates ##
    #########################################################
    radius = '20'

    # Station metadata API URL
    metadata_api = 'https://api.synopticlabs.org/v2/stations/metadata?&'

    # URL to be sent to API
    url = metadata_api + urllib.parse.urlencode({'token': token,'output': output, 'radius': latitude+','+longitude+','+radius, 'limit': '10', 'vars': 'wind_speed,wind_direction'})

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
    min_station_distance_index = station_index[min_station_distance_idx]
    closest_station = station_id[min_station_distance_idx]
 
    period_start = json_data['STATION'][min_station_distance_index]['PERIOD_OF_RECORD']['start']
    period_end = json_data['STATION'][min_station_distance_index]['PERIOD_OF_RECORD']['end']
    latitude_station = json_data['STATION'][min_station_distance_index]['LATITUDE']
    longitude_station = json_data['STATION'][min_station_distance_index]['LONGITUDE']

    # Convert time period to usable format
    year_start = period_start[:4]
    month_start = period_start[5:7]
    day_start = period_start[8:10]
    hour_start = period_start[11:13]
    minute_start = period_start[14:16]

    year_end = period_end[:4]
    month_end = period_end[5:7]
    day_end = period_end[8:10]
    hour_end = period_end[11:13]
    minute_end = period_end[14:16]

    start = year_start+month_start+day_start+hour_start+minute_start
    end = year_end+month_end+day_end+hour_end+minute_end

    print('Closest weather station with 10 years of wind speed data: ' + closest_station)
    print('Lat: ' + latitude_station + ' Long: ' + longitude_station)
    print('Distance from wind turbine: ' + str(min_station_distance) + ' miles')
    print('Avaiable time period: ' + period_start + ' to ' + period_end)
    print()

    df = pd.read_csv(closest_station+'.csv')

    shape, loc, scale  = genextreme.fit(df.wind_speed)
    print(shape)
    print(loc)
    print(scale)
    shape = float(shape)

    trace0 = go.Histogram(
        x=df.wind_speed,
        histnorm='probability',
        nbinsx = 50
        #bins = dict(
        #    start = 0,
        #    end = 10,
        #    size = .25
        #)
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

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)