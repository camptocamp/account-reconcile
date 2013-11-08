# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import unittest2
from datetime import datetime
from ..connector import iso8601_to_utc_datetime


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
