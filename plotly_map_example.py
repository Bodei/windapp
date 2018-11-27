import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import numpy as np
import urllib.parse
import requests
import json
import pandas as pd

df = pd.read_csv('turbine_locations.csv')
df['latitude']= df['latitude'].astype(str)
df['longitude']= df['longitude'].astype(str)
mapbox_access_token = 'pk.eyJ1IjoiY2JvZGVpIiwiYSI6ImNqbzY3eG4wejBlN3UzcXBiNTk1a3N4NWsifQ.rAUKKJtNfW5Mw2GX8Tdoag'
print(df.latitude)
data = {
    go.Scattermapbox(
        lat= df['latitude'].tolist(),
        lon = df['longitude'].tolist(),
        mode= 'markers',
    )
}

layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken = mapbox_access_token,
        center=dict(
            lat = 42.84,
            lon = -76.20
        ),
        pitch = 0,
        zoom = 12,
    ),
)

fig = dict(data=data, layout=layout)

plot(fig, filename='mapbox.html', auto_open=False)