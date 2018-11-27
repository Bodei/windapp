import urllib.parse
import requests
import json

station_id = 'A4448'

turbine_api = 'http://mybergey.aprsworld.com/data/jsonMyBergey.php?'
url = turbine_api + urllib.parse.urlencode({'station_id': station_id, 'statsHours': '72', '&_':'1542651912866' })
json_data = requests.get(url).json()

print(json_data['displayName'])
print(json_data['now_time'])
print(json_data['inverter_systemStateText'])
print(json_data['inverter_output_power'])