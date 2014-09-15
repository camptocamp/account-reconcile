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

{'name': 'QoQa Specific',
 'version': '0.0.2',
 'category': 'Others',
 'depends': ['sale',
             'product',
             'product_custom_attributes',
             'purchase',
             'crm_claim_rma',
             'delivery_carrier_label_postlogistics_shop_logo',
             'product_variant_simple',
             'qoqa_offer',
             'account_payment',
             'delivery_carrier_label_dispatch',
             ],
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'description': """
QoQa Specific
=============

Local customizations for QoQa.

Product:

set cost_method default to average

Stock.move:

Overwrite of do_partial to keep tracking id of unprocessed packs
""",
 'images': [],
 'demo': [],
 'data': ['security/security.xml',
          'stock_view.xml',
          'product_view.xml',
          'purchase_view.xml',
          'crm_claim_view.xml',
          'payment_view.xml',
          'account_invoice_view.xml',
          ],
 'installable': True,
 'application': True,
 }
