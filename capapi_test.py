import unittest
from capapi import *

'''
You must write unit tests to show that the data access, storage, and processing components of your project are working correctly.

You must create at least 3 test cases and use at least 15 assertions or calls to ‘fail( )’.

Your tests should show that you are able to access data from all of your sources, that your database is correctly constructed and can satisfy queries that are necessary for your program, and that your data processing produces the results and data structures you need for presentation.
'''

class TestAccess(unittest.TestCase):

    def test_cap_api(self):
        result = get_cap_data()

        self.assertIs(type(result), list)
        self.assertEqual(type(result[0]), tuple)
        self.assertGreaterEqual(len(result), 1000)

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

        self.assertGreaterEqual(len(result_list), 1000)

        statement = '''
        SELECT *
        FROM Cases
        WHERE CourtId NOT NULL
        '''
        results = cur.execute(statement)
        result_list = results.fetchall()

        self.assertGreaterEqual(len(result_list), 100)

class TestProcessing(unittest.TestCase):

    def test_cases_by_state(self):
        result = get_cases_by_state()

        self.assertIs(type(result), list)
        self.assertIs(type(result[0]), tuple)
        self.assertEqual(len(result[0]), 4) # (state_abbr, state_name, count, percent)
        self.assertGreater(result[0][2], 0) # should be a count
        self.assertLessEqual(result[0][3], 1) # should be a decimal

    def test_percent_with_word_by_state(self):
        common_word = "the"
        not_a_word = "eafndkgairw"
        result = get_percent_by_state_containing(common_word)
        null_result = get_percent_by_state_containing(not_a_word)

        self.assertIs(type(result), list)
        self.assertIs(type(result[0]), tuple)
        self.assertGreaterEqual(result[0][1], 0.5) # really hoping at least half have the word "the"...
        self.assertEqual(null_result[0][1], 0) # ...and that 0% "eafndkgairw"

    def test_list_of_cases_with_word(self):
        common_word = "has"
        not_a_word = "rnaciaetr"
        result = get_list_of_cases_containing(common_word)
        null_result = get_list_of_cases_containing(not_a_word)

        self.assertIs(type(result), list)
        self.assertGreaterEqual(len(result), 10)
        self.assertIs(type(result[0]), tuple)
        self.assertIs(len(result[0]), 6) # (state abbr, state name, case name, case abbr, court name, court abbr)

        self.assertIs(type(null_result), list) # still a list...
        self.assertEqual(len(null_result),0) # but no tuples in it

    def test_freq_of_words_by_time(self):
        list_of_words = ["the", "women", "arn4389fd"]

        result = get_freq_by_time_for(list_of_words)

        self.assertIs(type(result), list)
        self.assertEqual(len(result), 3)
        self.assertIs(type(result[0]), dict)
        # they should all have data for all dates
        self.assertEqual(len(result[0]), len(result[1]))
        self.assertEqual(len(result[1]), len(result[2]))

        for date in result[0]:
            self.assertNotEqual(result[0][date], 0) # "the" should show up every day

        for date in result[2]:
            self.assertEqual(result[2][date], 0) # that nonsense word shouldn't show up on any day!

unittest.main(verbosity=2)
