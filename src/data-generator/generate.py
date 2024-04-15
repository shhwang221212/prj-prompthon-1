import os

import requests
import pandas as pd
import xmltodict
import json

dict_list = []
OPEN_API_KEY = os.getenv("OPEN_API_KEY")

def read_csv():
    location_csv = pd.read_csv('../resource/location.csv')
    return location_csv

def append_loc_to_dict(location):
    area_nm = location[3]
    url = f'http://openapi.seoul.go.kr:8088/{OPEN_API_KEY}/xml/citydata_ppltn/1/5/{area_nm}'

    response = requests.get(url).content
    dict_type = xmltodict.parse(response)
    json_type = json.dumps(dict_type)
    dict2_type = json.loads(json_type)

    fcst_ppltn_list = dict2_type['Map']['SeoulRtd.citydata_ppltn']['FCST_PPLTN']['FCST_PPLTN']

    for fcst in fcst_ppltn_list:
        loc_info = generate_dict(location, fcst)
        dict_list.append(loc_info)

def generate_dict(location, fcst_ppltn):
    return {
        "장소코드" : location[2],
        "장소명": location[3],
        "시간대" : fcst_ppltn["FCST_TIME"],
        "혼잡수준" : fcst_ppltn["FCST_CONGEST_LVL"],
        "최소인원": fcst_ppltn["FCST_PPLTN_MIN"],
        "최대인원": fcst_ppltn["FCST_PPLTN_MAX"]
    }

if __name__ == '__main__':
    location = read_csv()
    loc_list = location.values.tolist()
    for loc in loc_list:
        append_loc_to_dict(loc)

    df = pd.DataFrame(dict_list)
    df.to_csv('../resource/result.csv')
