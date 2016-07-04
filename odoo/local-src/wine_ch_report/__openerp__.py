# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'Swiss Wine Reports',
 'version': '0.1',
 'category': '',
 'description': """

""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': [
     'report',
     'qoqa_product',
     'stock',
     ],
 'data': [
     'wizard/wine_ch_inventory_wizard_view.xml',
     'report/wine_move_analysis_view.xml',
     'report.xml',
     'views/report_wine_cscv_form.xml',
     'views/report_wine_inventory.xml',
     'security/ir.model.access.csv',
     ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 'css': [],
 }
