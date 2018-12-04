# SI507-Final-ebwydra

Work in progress...

## Data Sources

### Caselaw Access Project (CAP) API

The CAP API provides access to information about all 6,000,000+ official US court cases published in books from 1658 to 2018. More information about the CAP API can be found at the following link: https://case.law/api/.

The 'get_cap_data()' function makes a call to the CAP API 'cases' endpoint for information about 2,500 U.S. federal ('jurisdiction=us') court cases beginning on January 1, 2016 ('decision_date_min=2016-01-01'). Although some information about the cases is accessible without an API key, this project requests the full text of cases ('full_case=true') which requires authentication. The data obtained from the CAP API populates the 'Cases' table of the 'law.db' database.

A basic API key allows access to the full text of 500 cases per day (see https://case.law/api/#limits for details), but special researcher access is required for the volume of requests required by this program. The researcher API key should be entered into a file named 'secrets.py' that follows the structure of the 'secrets_example.py' file included in this repository.

### Wikipedia

The 'get_courts_data()' function scrapes the Wikipedia page 'List of United States district and territorial courts' (https://en.wikipedia.org/wiki/List_of_United_States_district_and_territorial_courts) for information about the 94 federal district and territorial courts in the United States, which presented in a table on Wikipedia. The data obtained from scraping Wikipedia populates the 'DistrictCourts' table of the 'law.db' database.

### CSV of U.S. states

The 'state_table.csv' file included in this repository was downloaded from https://statetable.com/ and contains structured information about 56 U.S. states and territories (including Washington, D.C.). This information is used to populate the 'States' table of the 'law.db' database.
