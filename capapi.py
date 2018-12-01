import requests
from bs4 import BeautifulSoup
import json
import csv
import sqlite3 as sqlite
from secrets import CAPAPI_TOKEN

DBNAME = 'law.db'
STATESCSV = 'state_table.csv'
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

def get_cap_data():

    url = "https://api.case.law/v1/cases/?full_case=true&jurisdiction=us&decision_date_min=2016-01-01"
    page = 0
    list_of_case_tups = []

    while page < 10: # I want the first 10 pages
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

        url = resp_dict['next']
        page += 1

        for case in resp_dict['results']: # there are 100 in a page
            name = case['name']
            name_abbr = case['name_abbreviation']
            date = case['decision_date']
            court = case['court']['name_abbreviation']
            text = ""
            for opinion in case['casebody']['data']['opinions']:
                text += opinion['text']

            case_tup = (name, name_abbr, date, court, text)
            list_of_case_tups.append(case_tup)

    return list_of_case_tups

''' Create database '''

def create_db():

    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    ''' Drop existing tables '''

    statement = "DROP TABLE IF EXISTS Cases"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS DistrictCourts"
    cur.execute(statement)
    # statement = "DROP TABLE IF EXISTS CircuitCourts"
    # cur.execute(statement)
    statement = "DROP TABLE IF EXISTS States"
    cur.execute(statement)

    conn.commit()

    ''' Create tables '''

    # Create States table
    statement = '''
    CREATE TABLE States (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Abbr TEXT,
	AssocPress TEXT,
	CensusRegionName TEXT,
	CensusDivisionName TEXT,
	CircuitCourt TEXT
    );
    '''
    cur.execute(statement)

    # Create DistrictCourts table
    statement = '''
    CREATE TABLE DistrictCourts (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    StateId INTEGER REFERENCES States(Id),
    CourtName TEXT,
    Citation TEXT,
    CircuitCourt TEXT,
    Established INTEGER,
    NumJudges INTEGER
    );
    '''
    cur.execute(statement)

    # Create Cases table
    statement = '''
    CREATE TABLE Cases (
    Id INTEGER PRIMARY KEY,
    Name TEXT,
    NameAbbr TEXT,
    DecisionDate INTEGER,
    CourtId INTEGER REFERENCES DistrictCourts(Id),
    CaseBody TEXT
    );
    '''
    cur.execute(statement)

    conn.commit()

    ''' Load data into tables '''

    # States table - from csv
    with open(STATESCSV, encoding = 'utf-8') as states_data:
        list_of_tuples = []

        csv_reader = csv.reader(states_data)
        for row in csv_reader:
            name = row[1]
            abbr = row[2]
            ap = row[10]
            region = row[13]
            division = row[15]
            circuit = row[16]
            tup = (name,abbr,ap,region,division,circuit)
            list_of_tuples.append(tup)

        for tup in list_of_tuples[1:]:
            statement = '''
            INSERT INTO States (Name, Abbr, AssocPress, CensusRegionName, CensusDivisionName, CircuitCourt)
            VALUES (?,?,?,?,?,?)
            '''
            cur.execute(statement, tup)
            conn.commit()

    # DistrictCourts table
    courts_list = get_courts_data() # list of tuples
    for court in courts_list:
        # Get State ID -- court[0]
        statement = '''
        SELECT Id
        FROM States
        WHERE Name LIKE \"{}\"
        '''.format(court[0])
        cur.execute(statement)
        result = cur.fetchone()
        try:
            id = result[0]
        except:
            id = None
        # print("{} {}".format(id, court[1]))
        court_l = list(court)
        court_l.append(id)
        court_l.remove(court_l[0]) # get rid of state name
        circuit = court_l[2].strip("abcdefghijklmopqrstuvwxyz")
        court_l.remove(court_l[2])
        court_l.append(circuit)
        new_tup = tuple(court_l)
        # print(new_tup)

        statement = '''
        INSERT INTO DistrictCourts (CourtName, Citation, Established, NumJudges, StateId, CircuitCourt)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        cur.execute(statement, new_tup)
        conn.commit()

    # Cases table
    cases_list = get_cap_data()
    for case in cases_list:
        # Get Court ID - (name, name_abbr, date, court, text) - case[3]
        statement = '''
        SELECT Id
        FROM DistrictCourts
        WHERE Citation LIKE \"{}\"
        '''.format(case[3])
        cur.execute(statement)
        result = cur.fetchone()
        try:
            id = result[0]
        except:
            id = None
        case_l = list(case)
        case_l.append(id)
        case_l.remove(case_l[3])
        new_tup = tuple(case_l)

        statement = '''
        INSERT INTO Cases (Name, NameAbbr, DecisionDate, CaseBody, CourtId)
        VALUES (?, ?, ?, ?, ?)
        '''
        cur.execute(statement, new_tup)
        conn.commit()

create_db()
