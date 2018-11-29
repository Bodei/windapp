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
    html.Iframe(id='plot',
                src = "//plot.ly/~cbodei/10.embed",
                width = '100%',
                height = '800',
    )
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('plot','src'),
    [Input('map','clickData')]
)

def update_plot(clickData):
    return clickData['points'][0]['text']

if __name__ == '__main__':
    app.run_server(debug=True)