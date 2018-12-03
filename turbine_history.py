import urllib.parse
import requests
import pandas as pd
from datetime import datetime
from dateutil import tz

def turbine_history(turbine_id):
    api = 'http://mybergey.aprsworld.com/data/json-history.php?'
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    d = []
    url = api + urllib.parse.urlencode({'station_id': turbine_id})+'&historyHours=72&_=1543611997109'
    json_data = requests.get(url).json()

    for i in range(0, int(len(json_data['block']))):
        d.append({'time': (datetime.utcfromtimestamp(int(float(json_data['block'][i]['block_timestamp'])))).replace(tzinfo=from_zone).astimezone(to_zone),
                'output': json_data['block'][i]['output_power_avg']})
    df = pd.DataFrame(d)
    if df.empty == True:
        d = {
            'time': [0],
            'output': [0]
        }
        df = pd.DataFrame(d)

    return df
#print(turbine_history('A4448'))