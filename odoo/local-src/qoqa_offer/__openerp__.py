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
             # Need to depend on sale_exception and disable all exceptions
             # in tests to avoid tests dependency problem.
             'sale_exception',
             'delivery',
             'ecotax',
             'procurement',
             'product_brand',  # oca/product-attribute
             # TODO: activate
             # 'picking_dispatch',  # stock-logistic-flows
             'batch_picking_group',
             ],
 'data': ['sale_order_view.xml',
          'account_invoice_view.xml',
          'stock_view.xml',
          'qoqa_offer_view.xml',
          'qoqa_shop_view.xml',
          'res_users_view.xml',
          'wizard/product_orderpoint_confirm_views.xml',
          'security/ir.model.access.csv',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 'css': ['static/src/css/qoqa_offer.css'],
 }
