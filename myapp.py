import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Residential Wind Turbine Monitor'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Iframe(id = 'map', srcDoc = open('my_map.html', 'r').read(), width = '100%', height = '600')
])

if __name__ == '__main__':
    app.run_server(debug=True)