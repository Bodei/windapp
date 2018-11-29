import urllib.parse
import requests
import folium
import json
import pandas as pd
import os
import altair as alt
from vega_datasets import data
import numpy as np

token = '0939c8c78a5a460e8685922d985d500f'  # API token
output = 'json'                            # Output format
#########################################################
## Find closest weather station to turbine coordinates ##
#########################################################
latitude = '42.19114469'
longitude = '-79.74591313'
radius = '20'

# Station metadata API URL
metadata_api = 'https://api.synopticlabs.org/v2/stations/metadata?&'

# URL to be sent to API
url = metadata_api + urllib.parse.urlencode({'token': token, 'output': output, 'radius': latitude +','+longitude+','+radius, 'limit': '10', 'vars': 'wind_speed,wind_direction'})

# API GET request
json_data = requests.get(url).json()
json_number_of_stations = json_data['SUMMARY']['NUMBER_OF_OBJECTS']
# print(json_data)
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
        station_distance.insert(i, json_station_distance)
        station_id.insert(i, json_station_id)
        station_index.insert(i, i)
if not station_distance:
    print('No weather stations within ' + radius +
              ' miles have 10 years of wind speed data, try increasing range.')
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
print('Distance from wind turbine: ' +
          str(min_station_distance) + ' miles')
print('Avaiable time period: ' + period_start + ' to ' + period_end)
print()

timeseries_api = 'https://api.synopticlabs.org/v2/stations/timeseries?&'
time_format = '%Y%m%d%H%M'

url = timeseries_api + urllib.parse.urlencode({'token': token, 'output': output, 'stid': closest_station, 'start': start,
                                                   'end': end, 'obtimezone': 'local', 'timeformat': time_format, 'vars': 'wind_speed,wind_direction'})
print(url)
json_data_wind = requests.get(url).json()
json_wind_speed = json_data_wind['STATION'][0]['OBSERVATIONS']['wind_speed_set_1']
json_wind_direction = json_data_wind['STATION'][0]['OBSERVATIONS']['wind_direction_set_1']
json_datetime = json_data_wind['STATION'][0]['OBSERVATIONS']['date_time']
station_data = {
    'date': json_datetime,
    'wind_speed': json_wind_speed,
    'wind_direction': json_wind_direction
}
df = pd.DataFrame(station_data)
df = df.dropna()
df = df[df['wind_speed'] < 10]
df = df[(df != 0.0).all(1)]
df.to_csv(closest_station+'.csv')