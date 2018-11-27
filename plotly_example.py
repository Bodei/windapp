import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import numpy as np
import urllib.parse
import requests
import json
import pandas as pd

url = 'http://pamsite.rutgers.edu/data_for_graphing/SW_diff_insolation.csv'
df = pd.read_csv(url)
trace0 = go.Scatter(
    x = df.Time,
    y = df.loc[:,' Total Insolation'],
    name = 'Total Insolation'
)
trace1 = go.Scatter(
    x = df.Time,
    y = df.loc[:,' Diffuse Insolation'],
    name = 'Diffuse Insolation'
)
trace2 = go.Scatter(
    x = df.Time,
    y = df.loc[:,' UV Insolation '],
    name = 'UV Insolation'
)

layout = go.Layout(
    xaxis=dict(
        type='date'
    )
)

data = [trace0, trace1, trace2]
fig = go.Figure(data=data, layout=layout)
plot(fig, filename='line.html', auto_open=False)