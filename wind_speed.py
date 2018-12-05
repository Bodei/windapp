import urllib.parse
import requests
import pandas as pd
import time
import datetime
import numpy as np
import pandas as pd

token = '0939c8c78a5a460e8685922d985d500f'
api = 'https://api.synopticdata.com/v2/stations/timeseries?'
radius = '14'

def wind_speed(latitude,longitude):
    url = api + urllib.parse.urlencode({
                                            'token': token,
                                            'units': 'metric',
                                            'radius': str(latitude)+','+str(longitude)+','+radius,
                                            'recent': '4320',
                                            'status': 'active',
                                            'vars': 'wind_speed,wind_gust,wind_direction',
                                            'limit': '1',
                                            'obtimezone': 'UTC',
                                            'output': 'json'})

    json_data = requests.get(url).json()
    try:
        json_wind_gust = json_data['STATION'][0]['OBSERVATIONS']['wind_gust_set_1']
        wind_gust= [0 if i is None else i for i in json_wind_gust]
        json_wind_speed = json_data['STATION'][0]['OBSERVATIONS']['wind_speed_set_1']
        wind_speed= [0 if i is None else i for i in json_wind_speed]
        date_time = json_data['STATION'][0]['OBSERVATIONS']['date_time']
    except:
        wind_gust = [0]
        wind_speed = [0]
        date_time = [0]
    d = {
        'wind_gust': wind_gust,
        'wind_speed': wind_speed,
        'date_time': date_time,
    }
    return pd.DataFrame(d)
#df = wind_gust('C7832')


