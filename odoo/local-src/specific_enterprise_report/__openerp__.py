# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
{'name': 'Customer specific enterprise reports',
 'version': '9.0.1.0.0',
 'category': 'other',
 'description': """
 Customer specific enterprise report

 Used to hide an enterprise menu at the moment
 """,
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com',
 'depends': ['account_reports',
             'specific_fct',
             ],
 'data': [
          'views/reports.xml',
          ],
 'test': [],
 'installable': True,
 'active': False,
 }
