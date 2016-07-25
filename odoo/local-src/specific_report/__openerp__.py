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
 - specific shipping default webkit labels
 - specific invoice report to fit with QoQa addresses
 - specific stock.location report "Stock Inventory Overview" with
   added description_warehouse info
 """,
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com',
 'depends': ['purchase',
             #'delivery_carrier_label_default_webkit',
             #'picking_dispatch',
             #'picking_dispatch_group',
             #'base_report_assembler'
             ],
 'data': [#'base_headers_data.xml',
          #'reports.xml',
          #'stock_report.xml',
          #'picking_dispatch_assemble.xml',
          #'security/ir.model.access.csv',
          'views/report_purchaseorder.xml',
          ],
 'test': [],
 'installable': True,
 'active': False,
 }
