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
{'name' : 'Swiss Wine Reports',
 'version' : '0.1',
 'category': '',
 'description': """
Swiss Wine Reports
==================

Add the reports for the "commission fédérale du commerce des vins (CFCV)".

It uses the custom attributes on the products to add the fields used in
the report only on products using a 'Wine' attribute set.

""",
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends' : [
     'base',
     'report_webkit',
     'product_custom_attributes',
     'stock',
     ],
 'data': [
     'wizard/wine_ch_inventory_wizard_view.xml',
     'report.xml',
     'wine_view.xml',
     'wine_data.xml',
     ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 'css': [],
 }
