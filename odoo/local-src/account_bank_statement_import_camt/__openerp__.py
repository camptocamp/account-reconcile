# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# flake8: noqa
# (since it is Odoo's code backported, it won't be PEP8)

{
    'name': 'Import CAMT Bank Statement',
    'category': 'Accounting & Finance',
    'depends': ['account_bank_statement_import'],
    'description': """
Module to import CAMT bank statements (BACKPORT FROM ENTERPRISE V10.0!!!).
======================================

Improve the import of bank statement feature to support the SEPA recommanded Cash Management format (CAMT.053).

THIS MODULE IS A BACKPORT OF A MODULE IN ODOO ENTERPRISE 10.0. IT SHOULD NOT BE PUBLISHED ELSEWHERE,
THE LICENSE FORBIDS IT.
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/camt_partners.xml',
        'data/account_bank_statement_camt.xml',
        'data/account_bank_statement_import_data.xml',
        'views/account_bank_statement_camt.xml',
    ],
    'license': 'OEEL-1',
    'installable': True,
}
