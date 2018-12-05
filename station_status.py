import urllib.parse
import requests
import pandas as pd

token = '0939c8c78a5a460e8685922d985d500f'
api = 'https://api.synopticdata.com/v2/stations/latest?'
radius = '14'

def station_status(latitude,longitude):
    url = api + urllib.parse.urlencode({
                                            'token': token,
                                            'units': 'metric',
                                            'radius': str(latitude)+','+str(longitude)+','+radius,
                                            'obtimezone': 'UTC',
                                            'within': '60',
                                            'status': 'active',
                                            'limit': '1',
                                            'vars': 'wind_speed,wind_gust,wind_direction',
                                            'output': 'json'})
    json_data = requests.get(url).json()
    #print(json_data)
    try:
        name = json_data['STATION'][0]['NAME']
    except:
        name = 'NaN'
    try:
        station_id = json_data['STATION'][0]['STID']
    except:
        station_id = 'NaN'
    try:
        wind_speed = json_data['STATION'][0]['OBSERVATIONS']['wind_speed_value_1']['value']
    except:
        wind_speed = 'NaN'
    try:
        wind_gust = json_data['STATION'][0]['OBSERVATIONS']['wind_gust_value_1']['value']
    except:
        wind_gust ='NaN'
    try:
        wind_direction = json_data['STATION'][0]['OBSERVATIONS']['wind_cardinal_direction_value_1d']['value']
    except:
        wind_direction = 'NaN'
    d = {
        'Name': name,
        'Station ID': station_id,
        'Wind Speed': wind_speed,
        'Wind Gust': wind_gust,
        'Wind Direction': wind_direction
    }
    return pd.DataFrame(d, index=[0])
#print(station_status('KSDC'))