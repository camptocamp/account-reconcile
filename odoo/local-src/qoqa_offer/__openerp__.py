# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'QoQa Offers',
 'version': '9.0.2.0.0',
 'category': '',
 'description': """
QoQa Offer
=========

Adds *Offer* models.


""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['sale',
             'sale_stock',
             'delivery',
             'ecotax',
             'procurement',
             # TODO: activate
             # 'picking_dispatch',  # stock-logistic-flows
             ],
 'data': ['qoqa_shop_view.xml',
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
