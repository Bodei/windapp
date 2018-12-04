import urllib.parse
import requests
import pandas as pd
import time
import datetime
import numpy as np

token = '0939c8c78a5a460e8685922d985d500f'
api = 'https://api.synopticdata.com/v2/stations/timeseries?'

def expected_power(station):
    try:
        url = api + urllib.parse.urlencode({
                                            'token': token,
                                            'stid': station,
                                            'units': 'metric',
                                            'recent': '4320',
                                            'vars': 'wind_gust',
                                            'obtimezone': 'UTC',
                                            'output': 'json'})

        json_data = requests.get(url).json()

        list_one = json_data['STATION'][0]['OBSERVATIONS']['wind_gust_set_1']
        list_two = [i * 2 for i in list_one]
        list_three = [int(round(i, 0)) for i in list_two]
        wind_speed = [i / 2 for i in list_three]

        d= ({'time': json_data['STATION'][0]['OBSERVATIONS']['date_time'],
        'wind_speed': wind_speed})
        df = pd.DataFrame(d)

        lookup = pd.read_csv('data/power_curve.csv')
        power_output = []
        for i in df.wind_speed:
            power_output.append(lookup.power_output[lookup.wind_speed[lookup.wind_speed == i].index.tolist()].tolist())

        power_output = [i for sublist in power_output for i in sublist]

        d2 = ({'time': df.time, 'power': power_output})
        #df2 = pd.DataFrame(d2)
    except:
        d2 = ({'time': [], 'power': []})
    df = pd.DataFrame(d2)
    return df