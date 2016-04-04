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

{'name': 'QoQa Connector',
 'version': '0.0.1',
 'category': 'Connector',
 'depends': ['connector',
             'connector_ecommerce',
             'sale_stock',
             'qoqa_offer',
             'qoqa_base_data',
             ],
 'external_dependencies': {
     'python': ['requests',
                'dateutil',
                ],
 },
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'description': """
QoQa Connector
==============

Synchronize OpenERP with the different QoQa Stores
(qoqa.ch, qwine.ch, qsport.ch, qooking.ch).

""",
 'images': [],
 'demo': [],
 'data': ['data.xml',
          'wizard/qoqa_backend_oauth_view.xml',
          'qoqa_backend/qoqa_backend_view.xml',
          'qoqa_shop/qoqa_shop_view.xml',
          'qoqa_offer/offer_view.xml',
          'qoqa_menu.xml',
          'product/product_view.xml',
          'partner/res_partner_view.xml',
          'address/res_partner_view.xml',
          'sale/sale_view.xml',
          'static_binding/res_company_view.xml',
          'static_binding/account_tax_view.xml',
          'static_binding/res_lang_view.xml',
          'static_binding/res_country_view.xml',
          'static_binding/res_currency_view.xml',
          'static_binding/payment_method_view.xml',
          'static_binding/delivery_carrier_view.xml',
          'qoqa_buyphrase/qoqa_buyphrase_view.xml',
          'product_attribute/product_attribute_view.xml',
          'security/ir.model.access.csv',
          'company_view.xml',
          ],
 'installable': True,
 'application': True,
 }
