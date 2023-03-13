import os
import openai
import requests
from urllib.parse import urlencode
import json
import httpx
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

# openai.api_key = os.getenv("OPENAI_KEY")
# openai.api_key = st.write()
openai.api_key = st.write(st.secrets['OPENAI_KEY'])

def get_response(INPUT):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": INPUT}
        ])
    message = response.choices[0]['message']

    return message


def get_assistant_msg(message):
    return "{}: {}".format(message['role'], message['content'])

def get_zip_code(message):
    parse = message['content'].split('-')
    zipcode = parse[0].split(' ')[0]
    return zipcode



def request_zillow_page(zipcode):
    BASE_HEADERS = {
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    URL = "https://www.zillow.com/homes/{}_rb/".format(str(zipcode))
    page = requests.get(URL, headers=BASE_HEADERS)
    return page


def parse_coords(page):
    s = page.text
    
    # find index of coordinates
    coords_dict = {}
    west = s.find("var westLng =")
    east = s.find("var eastLng =")
    north = s.find("var northLat =")
    south = s.find("var southLat =")
    


    # return coords_dict

    def getSubString(ch1, ch2, s):
        return s[s.find(ch1)+1:s.find(ch2)]

    east_long = s[east:east+28]
    west_long = s[west:west+28]
    north_lat = s[north:north+28]
    south_lat = s[south:south+28]
    # print("1:" , east_long, west_long, north_lat, south_lat)

    east_long_2 = getSubString("=", ";", east_long)
    west_long_2 = getSubString("=", ";", west_long)
    north_lat_2 = getSubString("=", ";", north_lat)
    south_lat_2 = getSubString("=", ";", south_lat)
    coords_dict['west'] = west_long_2
    coords_dict['east'] = east_long_2
    coords_dict['north'] = north_lat_2
    coords_dict['south'] = south_lat_2
    return coords_dict


def pull_zillow_records(coords_dict):


    east = coords_dict['east']
    west = coords_dict['west']
    south = coords_dict['south']
    north = coords_dict['north']
    # we should use browser-like request headers to prevent being instantly blocked
    BASE_HEADERS = {
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }


    url = "https://www.zillow.com/search/GetSearchPageState.htm?"
    parameters = {
        "searchQueryState": {
            "pagination": {},
            # "usersSearchTerm": "Park City UT 84060",
            # map coordinates that indicate New Haven city's area
            "mapBounds": {
                "west": west,
                "east": east,
                "south": south,
                "north": north,
            },
        },
        "wants": {
            # cat1 stands for agent listings
            "cat1": ["mapResults"]
            # and cat2 for non-agent listings
            # "cat2":["mapResults"]
        },
        "requestId": 2,
    }
    response = httpx.get(url + urlencode(parameters), headers=BASE_HEADERS)
    # data = response.json()
    results = response.json()["cat1"]["searchResults"]["mapResults"]
    # return json.dumps(results, indent=2)
    return results

def return_zillow_links(results, num_results):

    list_add = []
    for i in range(len(results[0:num_results])-1):
        # print("https://www.zillow.com/"+results[i]['detailUrl'])
        list_add.append("https://www.zillow.com/"+results[i]['detailUrl'])
    return list_add


def return_df(results):

    dfs = []
    for i in results:
        try:
            # print(i)
            new_record = {}
            homeInfo = i['hdpData']['homeInfo']

            new_record['city' ] = homeInfo['city']
            new_record['state'] = homeInfo['state']
            new_record['price'] = i['price']
            new_record['beds'] = i['beds']
            new_record['baths'] = i['baths']
            new_record['area_sq_ft'] = i['area']
            new_record['zillow_link'] = "https://www.zillow.com/" + i['detailUrl']
            dfs.append(new_record)
        except:
            # print("except: ", i)
            continue
    # print(dfs)
    columns = ['city', 'state', 'price', 'beds', 'baths', 'area_sq_ft', 'zillow_link']
    df = pd.DataFrame(dfs, columns=columns)
    return df[:10]



