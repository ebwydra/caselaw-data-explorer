import unittest
from capapi import *

'''
You must write unit tests to show that the data access, storage, and processing components of your project are working correctly. You must create at least 3 test cases and use at least 15 assertions or calls to ‘fail( )’. Your tests should show that you are able to access data from all of your sources, that your database is correctly constructed and can satisfy queries that are necessary for your program, and that your data processing produces the results and data structures you need for presentation.
'''

class TestAccess(unittest.TestCase):

    def test_cap_api(self):
        result = get_cap_data()

        self.assertIs(type(result), list)
        self.assertEqual(type(result[0]), tuple)
        self.assertEqual(len(result), 1000)

    def test_wiki_scrape(self):
        result = get_courts_data()

        self.assertIs(type(result), list)
        self.assertEqual(type(result[0]), tuple)
        self.assertEqual(len(result), 94)

class TestStorage(unittest.TestCase):

    def test_states_table(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
        statement = '''SELECT Name FROM States'''
        results = cur.execute(statement)
        result_list = results.fetchall()

        self.assertIn(('Massachusetts',), result_list)
        self.assertGreaterEqual(len(result_list), 50)

    def test_courts_table(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
        statement = '''SELECT * FROM DistrictCourts'''
        results = cur.execute(statement)
        result_list = results.fetchall()

        self.assertEqual(len(result_list), 94)

        statement = '''
        SELECT *
        FROM DistrictCourts
        JOIN States
        ON DistrictCourts.StateId = States.Id
        '''
        results = cur.execute(statement)
        result_list = results.fetchall()

        self.assertGreaterEqual(len(result_list), 91) # 91 district courts (I don't care about the 3 territorial courts)

    def test_cases_table(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
        statement = '''SELECT * FROM Cases'''
        results = cur.execute(statement)
        result_list = results.fetchall()

        self.assertEqual(len(result_list), 1000)

        statement = '''
        SELECT *
        FROM Cases
        WHERE CourtId NOT NULL
        '''
        results = cur.execute(statement)
        result_list = results.fetchall()

        self.assertGreaterEqual(len(result_list), 100)

class TestProcessing(unittest.TestCase):

    pass

unittest.main(verbosity=2)
