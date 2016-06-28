# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'Swiss Wine Reports',
 'version': '0.1',
 'category': '',
 'description': """
Swiss Wine Reports
==================

Add the reports for the "commission fédérale du commerce des vins (CFCV)".

It uses the custom attributes on the products to add the fields used in
the report only on products using a 'Wine' attribute set.

""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': [
     #'product_custom_attributes',
     'report',
     'qoqa_product',
     'stock',
     ],
 'data': [
     'wizard/wine_ch_inventory_wizard_view.xml',
     'report/wine_move_analysis_view.xml',
     'report.xml',
     'views/report_wine_cscv_form.xml',
     'security/ir.model.access.csv',
     ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 'css': [],
 }
