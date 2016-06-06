# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'QoQa Connector',
 'version': '9.0.2.0.0',
 'category': 'Connector',
 'depends': ['connector',
             'qoqa_base_data',
             'delivery',
             'connector_base_product',
             'account_payment_mode',  # oca/bank-payment
             'account_payment_sale',  # oca/bank-payment
             'connector_ecommerce',   # oca/connector-ecommerce
             'sale_exception',        # oca/sale-workflow
             'sale_stock',
             'qoqa_offer',
             'qoqa_product',
             ],
 'external_dependencies': {
     'python': ['requests',
                'dateutil',
                ],
 },
 'pre_init_hook': 'pre_init_hook',
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
 'data': [
          'data.xml',
          'wizard/qoqa_backend_auth_view.xml',
          'qoqa_backend/qoqa_backend_view.xml',
          'qoqa_shop/qoqa_shop_view.xml',
          'qoqa_offer/offer_view.xml',
          'sale/sale_view.xml',
          'qoqa_menu.xml',
          'product_product/product_view.xml',
          'product_template/product_template_view.xml',
          'partner/res_partner_view.xml',
          'address/res_partner_view.xml',
          'res_company/res_company_view.xml',
          'account_tax/account_tax_view.xml',
          'res_country/res_country_view.xml',
          'res_currency/res_currency_view.xml',
          'account_payment_mode/account_payment_mode_views.xml',
          'delivery_carrier/delivery_carrier_view.xml',
          'security/ir.model.access.csv',
          ],
 'installable': True,
 'application': True,
 }
