# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import unittest2
from datetime import datetime
from ..connector import iso8601_to_utc_datetime, utc_datetime_to_iso8601


class test_iso8601(unittest2.TestCase):

    def test_iso8601_to_utc(self):
        """ convert an iso8601 date to UTC """
        date = '2013-11-04T13:52:01+0100'
        utc_date = iso8601_to_utc_datetime(date)
        expected = datetime(2013, 11, 04, 12, 52, 01)
        self.assertEquals(utc_date, expected)

    def test_iso8601_notz_to_utc(self):
        """ convert an iso8601 date without timezone to UTC """
        date = '2013-11-04T13:52:01'
        utc_date = iso8601_to_utc_datetime(date)
        expected = datetime(2013, 11, 04, 13, 52, 01)
        self.assertEquals(utc_date, expected)

    def test_date_to_iso8601(self):
        """ convert a date to iso8601 """
        date = datetime(2013, 11, 04, 13, 52, 01)
        iso_date = utc_datetime_to_iso8601(date)
        expected = '2013-11-04T13:52:01+00:00'
        self.assertEquals(iso_date, expected)
