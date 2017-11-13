"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from accountifie.cal import *
from accountifie.cal.models import Day, Month, Year, Week, Quarter
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class CalendarTests(TestCase):
    def test_populate_calendar(self):
        populate()
        self.assertTrue(Day.objects.count() in [365, 366])
        self.assertTrue(Week.objects.count() in [52, 53, 54])
        self.assertEqual(Month.objects.count(), 12)
        self.assertEqual(Quarter.objects.count(), 4)
        self.assertEqual(Year.objects.count(), 1)

    def test_regex_periods(self):
        self.assertTrue(PAT_YEAR.match('2014'))
        self.assertFalse(PAT_YEAR.match('99'))
        self.assertFalse(PAT_YEAR.match('12345'))

        self.assertTrue(PAT_QUARTER.match('2014Q1'))
        self.assertTrue(PAT_QUARTER.match('2014Q4'))
        self.assertFalse(PAT_QUARTER.match('2014Q5'))

        self.assertTrue(PAT_HALF.match('2014H1'))
        self.assertTrue(PAT_HALF.match('2014H2'))
        self.assertFalse(PAT_HALF.match('2014H3'))

        self.assertTrue(PAT_MONTH.match('2014M01'))
        self.assertTrue(PAT_MONTH.match('2014M12'))

        self.assertFalse(PAT_MONTH.match('2014M7'))
        self.assertFalse(PAT_MONTH.match('2014M00'))
        self.assertFalse(PAT_MONTH.match('2014M13'))


        self.assertTrue(PAT_WEEK.match('2014W01'))
        self.assertFalse(PAT_WEEK.match('2014W00'))
        self.assertFalse(PAT_WEEK.match('2014W54'))



    def test_period_ids(self):
        "Useful as query params, check if valid date range"
        for thing in ['2014Q1', '2013M07', '2012Q4', '2014W36']:
            self.assertTrue(is_period_id(thing))

        for thing in [None, '', 201, 12345, '99', '2013M00', '2012Q5', '2014W56', '2014H0']:
            self.assertFalse(is_period_id(thing), "is_period_id('%s') succeeded unexpectedly" % thing)


        self.assertTrue(is_iso_date("2014-08-31"))
        self.assertFalse(is_iso_date("31/8/2014"))

    def test_start_of_period(self):
        
        for thing, expected in [
            ['2014M01', date(2014,1,1)],
            ['2014M03', date(2014,3,1)],
            ['2014M04', date(2014,4,1)],
            ['2014M12', date(2014,12,1)],

            ['2014Q1', date(2014,1,1)],
            ['2014Q2', date(2014,4,1)],
            ['2014Q3', date(2014,7,1)],
            ['2014Q4', date(2014,10,1)],

            ['2014H1', date(2014,1,1)],
            ['2014H2', date(2014,6,1)],

            ['2014', date(2014,1,1)],
            ]:
            self.assertEqual(start_of_period(thing), expected)


    def test_end_of_period(self):
        
        for thing, expected in [
            ['2014M01', date(2014,1,31)],
            ['2014M03', date(2014,3,31)],
            ['2014M04', date(2014,4,30)],
            ['2014M12', date(2014,12,31)],

            ['2014Q1', date(2014,3,31)],
            ['2014Q2', date(2014,6,30)],
            ['2014Q3', date(2014,9,30)],
            ['2014Q4', date(2014,12,31)],

            ['2014H1', date(2014,6,30)],
            ['2014H2', date(2014,12,31)],

            ['2014', date(2014,12,31)],
            ]:
            self.assertEqual(end_of_period(thing), expected)


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True

Calendar tests:

>>> from docengine.cal import previous_period, next_period
>>> previous_period("2014W22")
"2014W21"
>>> previous_period("2014W01")
"2013W52"
>>> previous_period("2014M01")
"2013M12"
>>> previous_period("2014Q1")
"2013Q4"
>>> previous_period("2014H1")
"2013H2"

>>> next_period("2014W22")
"2014W23"
>>> next_period("2014W52")
"2015W01"
>>> next_period("2014Q4")
"2015Q1"
>>> next_period("2014H2")
"2015H1"
>>> next_period("2014M12")
"2015M01"




"""}

