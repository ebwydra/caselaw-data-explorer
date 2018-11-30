import requests
from bs4 import BeautifulSoup
import json
import csv
import sqlite3 as sqlite
from secrets import CAPAPI_TOKEN

''' Caching setup '''

CACHE_FNAME = "cache.json"
try:
    f = open(CACHE_FNAME, 'r')
    f_contents = f.read()
    f.close()
    CACHE_DICTION = json.loads(f_contents)
except:
    CACHE_DICTION = {}

''' Functions that get data from the internet '''

def get_courts_data():
    list_of_courts = []

    url = 'https://en.wikipedia.org/wiki/List_of_United_States_district_and_territorial_courts'

    if url in CACHE_DICTION:
        # print("Getting cached data")
        html = CACHE_DICTION[url]
    else:
        # print("Getting new data")
        html = requests.get(url).text
        CACHE_DICTION[url] = html
        f = open(CACHE_FNAME, 'w')
        f.write(json.dumps(CACHE_DICTION))
        f.close

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("table", class_="wikitable sortable")
    row_set = table.find_all("tr")

    for row in row_set[1:]:
        td_set = row.find_all("td")

        name_list = td_set[0].text.split()
        if name_list[-1] == "Columbia":
            state = "District of Columbia"
        elif name_list[-2] != "of":
            state = "{} {}".format(name_list[-2], name_list[-1])
        else:
            state = name_list[-1]

        name = td_set[0].text.strip()
        cite = td_set[1].text.strip()
        appeals = td_set[2].text.strip()
        estd = td_set[3].text.strip()
        judges = td_set[4].text.strip()

        tup = (state,name,cite,appeals,estd,judges)
        list_of_courts.append(tup)

    return list_of_courts

def get_cap_data(url):
    if url in CACHE_DICTION:
        # print("Getting cached data")
        resp_dict = CACHE_DICTION[url]
    else:
        # print("Getting new data")
        resp = requests.get(url, headers = {'Authorization': CAPAPI_TOKEN})
        resp_dict = json.loads(resp.text)
        CACHE_DICTION[url] = resp_dict
        f = open(CACHE_FNAME, 'w')
        f.write(json.dumps(CACHE_DICTION))
        f.close
    return resp_dict

first_url = "https://api.case.law/v1/cases/?full_case=true&jurisdiction=us"

# data = get_cap_data(first_url)
# print(type(data))
# print(data['count']) # 1700254
# print(data['next']) # https://api.case.law/v1/cases/?cursor=cD0xNzk1LTAxLTAx&full_case=true&jurisdiction=us
# print(data['previous'])
# print(len(data['results']))
