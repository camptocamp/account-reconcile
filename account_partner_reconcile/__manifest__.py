# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Partner Reconciliation',
    'summary': 'Allows run reconciliation only for same partner',
    'version': '10.0.1.0.0',
    'depends': ['account'],
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': 'http://www.github.com/OCA/account-reconcile',
    'category': 'Finance',
    'license': 'AGPL-3',
    'data': [
        'report/account_move_lines_report.xml',
    ],
    'installable': True,
}
