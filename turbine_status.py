import urllib.parse
import requests
import json
import pandas as pd

def turbine_status(turbine_id):
    turbine_id = str(turbine_id)

    turbine_api_status = 'http://mybergey.aprsworld.com/data/jsonMyBergey.php?'
    turbine_api_data  = 'http://mybergey.aprsworld.com/data/ps2/rawData.php?'
    url_one = turbine_api_status + urllib.parse.urlencode({
                                                'station_id': turbine_id,
                                                'statsHours': '72', 
                                                '&_':'1542651912866' 
                                               })
    url_two = turbine_api + urlib.parse.urlencode({
                                                'station_id': turbine_id,
                                                'packet_date': '2018-06-30i%2000:00:00'
                                                'hours_before': '0'
                                                'hours_after': '1'
                                                'csv': 1
                                                })
    df = pd.read_csv(url_two)
    print(df)



    json_data = requests.get(url_one).json()

    print(json_data['displayName'])
    print(json_data['now_time'])
    print(json_data['inverter_systemStateText'])
    print(json_data['inverter_output_power'])
turbine_status('A4441')
