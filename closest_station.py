import urllib.parse
import requests
import folium
import json
import pandas as pd
import os
import altair as alt
from vega_datasets import data
import numpy as np

token = '0939c8c78a5a460e8685922d985d500f' # API token
output = 'json'                            # Output format

def closest_station(latitude, longitude):

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

    #print('Closest weather station with 10 years of wind speed data: ' + closest_station)
    #print('Lat: ' + latitude_station + ' Long: ' + longitude_station)
    #print('Distance from wind turbine: ' + str(min_station_distance) + ' miles')
    #print('Avaiable time period: ' + period_start + ' to ' + period_end)
    #rint()

    # Create dictionary of data #
    d = dict()
    d['turbine_latitude'] = latitude
    d['turbine_longitude'] = longitude
    d['station_latitude'] = latitude_station
    d['station_longitude'] = longitude_station
    d['closest_station'] = closest_station
    d['min_station_distance'] = min_station_distance
    d['start'] = start
    d['end'] = end

    return d

    ############################################
    ## Pull data from closest weather station ##
    ############################################

def retrieve_station_data(closest_station, start, end):

    timeseries_api = 'https://api.synopticlabs.org/v2/stations/timeseries?&'
    time_format = '%Y%m%d%H%M'

    url = timeseries_api + urllib.parse.urlencode({'token': token,'output': output,'stid': closest_station, 'start': start, 'end':end, 'obtimezone': 'local', 'timeformat': time_format, 'vars': 'wind_speed,wind_direction'})

    json_data_wind = requests.get(url).json()
    json_wind_speed = json_data_wind['STATION'][0]['OBSERVATIONS']['wind_speed_set_1']
    json_wind_direction = json_data_wind['STATION'][0]['OBSERVATIONS']['wind_direction_set_1']
    json_datetime = json_data_wind['STATION'][0]['OBSERVATIONS']['date_time']

    station_data = {
        'date': json_datetime,
        'wind_speed': json_wind_speed,
        'wind_direction': json_wind_direction
    }
    df_station_data = pd.DataFrame(station_data)

    return df_station_data

def plot_map(latitude, longtitude, latitude_station, longtitude_station, wind_speed):

    ###################################
    ## Dataframe data to json format ##
    ###################################

    # Remove zeros
    wind_speed = wind_speed[(wind_speed != 0.0).all(1)]
    
    # Create histogram chart
    histogram = alt.Chart(df).mark_bar().encode(
        alt.X("wind_speed:Q", 
        bin=alt.BinParams(maxbins=100), 
        scale=alt.Scale(domain=(0, 14))),
        y='count(*):Q',).properties(
        width=400,
        height=200
    )

    rule = alt.Chart().mark_rule().encode(
        alt.X('mean(wind_speed):Q',
        scale=alt.Scale(domain=(0, 14))),
        size = alt.value(3)).properties(
        width=400,
        height=200
    )

    chart = histogram | rule

    # Convert chart it to JSON.
    alt.data_transformers.enable('json')
    chart_json = chart.to_json()

    ##########################################
    ## Plot weather station location on map ##
    ##########################################

    folium_map = folium.Map(
        location=[float(latitude_station), float(longtitude_station)],
        zoom_start=13,
        tiles="Stamen Terrain"
    )

    # Marker for station
    marker_station = folium.Marker(
        location=[float(latitude_station), float(longtitude_station)],
        popup=folium.Popup(max_width=450).add_child(
            folium.VegaLite(json.loads(chart_json), width=450, height=250)),
        icon=folium.Icon(color='blue', icon='cloud')
    )

    
    # Marker for turbine
    marker_turbine = folium.Marker(
        location=[float(latitude), float(longtitude)],
        popup='Wind Turbine',
        icon=folium.Icon(color='green')
    )

    # Add markers to map
    marker_station.add_to(folium_map)
    marker_turbine.add_to(folium_map)
    
    # Save map
    folium_map.save("my_map.html")

####################################
## Testing Functions and map plot ##
####################################

# Load turbine locations
df = pd.read_csv('turbine_locations.csv')
data= []
for row in df.itertuples():
    data.append(closest_station(str(getattr(row, 'latitude')), str(getattr(row, 'longitude'))))
df2 = pd.DataFrame(data)
#print(df)

df2[['turbine_latitude', 'turbine_longitude']] = df2[['turbine_latitude', 'turbine_longitude']].astype(float)
df2[['station_latitude', 'station_longitude']] = df2[['station_latitude', 'station_longitude']].astype(float)

turbine_locations = df2[['turbine_latitude','turbine_longitude']]
station_locations = df2[['station_latitude','station_longitude']]
station_ids = df2['closest_station']

turbine_locationlist = turbine_locations.values.tolist()
station_locationlist = station_locations.values.tolist()
station_idslist  = station_ids.values.tolist()
station_locationlist = [list(x) for x in set(tuple(x) for x in station_locationlist)]
station_idslist = [list(x) for x in set(tuple(x) for x in station_idslist)]
print(station_idslist)
map = folium.Map(
    location=[42.84821336, -76.20115378],
    zoom_start=8,
    tiles="Stamen Terrain"
    )

for point in range(0, len(turbine_locationlist)):
    folium.Marker(
        location=turbine_locationlist[point],
        popup=df['turbine_id'][point],
        icon=folium.Icon(color='red')
    ).add_to(map)

#for point in range(0, len(station_locationlist)):
    #folium.Circle(
    #    radius=15*1609.34,
     #   location=station_locationlist[point],
        #popup=str(station_idslist[point]),
    #    color='#3186cc',
    #    fill=True,
     #   fill_color='#3186cc'
    #)

for point in range(0, len(station_locationlist)):
    folium.Marker(
        location=station_locationlist[point],
        icon=folium.Icon(icon='cloud')
    ).add_to(map)

folium.LayerControl().add_to(map)
map.save("my_map.html")
