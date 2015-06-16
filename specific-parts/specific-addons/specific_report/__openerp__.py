# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013-2014 Camptocamp SA
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

{'name': 'Customer small specific report',
 'version': '1.1.0',
 'category': 'other',
 'description': """
 Customer specific report

 Contains:
 - specific report headers
 - specific shipping default webkit labels
 - specific invoice report to fit with QoQa addresses
 - specific stock.location report "Stock Inventory Overview" with
   added description_warehouse info
 """,
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com',
 'depends': ['base_headers_webkit',
             'delivery_carrier_label_default_webkit',
             'picking_dispatch',
             'purchase_order_webkit',
             'base_report_assembler'],
 'data': ['base_headers_data.xml',
          'reports.xml',
          'stock_report.xml',
          'picking_dispatch_assemble.xml',
          'security/ir.model.access.csv',
          ],
 'test': [],
 'installable': True,
 'active': False,
 }
