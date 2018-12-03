import urllib.parse
import requests
import pandas as pd

token = '0939c8c78a5a460e8685922d985d500f' # API token
output = 'json'                            # Output format

def closest_station(latitude, longitude):

    #########################################################
    ## Find closest weather station to turbine coordinates ##
    #########################################################
    radius = '30'

    # Station metadata API URL
    metadata_api = 'https://api.synopticlabs.org/v2/stations/metadata?&'

    # URL to be sent to API
    url = metadata_api + urllib.parse.urlencode({'token': token,'output': output, 'radius': str(latitude)+','+str(longitude)+','+radius, 'limit': '10', 'vars': 'wind_speed,wind_gust'})

    # API GET request
    json_data = requests.get(url).json()
    json_number_of_stations = json_data['SUMMARY']['NUMBER_OF_OBJECTS']
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
    closest_station = station_id[min_station_distance_idx]
 
    return closest_station