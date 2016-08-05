# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'Customer small specific report',
 'version': '9.0.1.0.0',
 'category': 'other',
 'description': """
 Customer specific report

 Contains:
 - specific report headers
 - specific shipping default qweb labels
 - specific invoice report to fit with QoQa addresses
 """,
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com',
 'depends': ['purchase',
             'connector_qoqa',
             'specific_fct',
             'delivery_carrier_label_default',
             ],
 'data': [#'reports.xml',
          'views/report_purchaseorder.xml',
          'views/report_accountinvoice.xml',
          'views/report_default_shipping_label.xml',
          ],
 'test': [],
 'installable': True,
 'active': False,
 }
