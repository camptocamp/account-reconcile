# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
{'name': 'QoQa Offers with Historical Margin',
 'version': '1.0',
 'category': '',
 'description': """
QoQa Offer
=========

Adds historical margin to *Offer* models.
""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['qoqa_offer',
             'product_historical_margin',
             ],
 'data': ['qoqa_offer_view.xml',
          'account_invoice_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': False,
 'css': [],
 }
