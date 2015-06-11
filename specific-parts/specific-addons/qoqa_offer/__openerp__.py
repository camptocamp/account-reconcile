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
{'name': 'QoQa Offers',
 'version': '1.2',
 'category': '',
 'description': """
QoQa Offer
=========

Adds *Offer* models.

A Offer is a sell of one to many positions over a given time period.
A position has, roughly, a price and a quantity for a product template,
when a product has variants, a position may sell several of them.

""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['sale',
             'sale_stock',
             'delivery',
             'product_variant_simple',  # specific-addons
             'picking_dispatch',  # stock-logistic-flows
             'ecotax',
             'procurement',
             'web_warning_on_save',
             ],
 'data': ['qoqa_offer_data.xml',
          'sale_order_view.xml',
          'account_invoice_view.xml',
          'stock_view.xml',
          'qoqa_offer_view.xml',
          'qoqa_buyphrase_view.xml',
          'delivery_carrier_view.xml',
          'procurement_view.xml',
          'security/ir.model.access.csv',
          'res_users_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 'css': ['static/src/css/qoqa_offer.css'],
 }
