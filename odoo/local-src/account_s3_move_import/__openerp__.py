# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'S3 move import',
    'version': '9.0.1.0.0',
    'category': 'Finance',
    'author': 'Camptocamp SA',
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'depends': [
        'account_move_transactionid_import',
        'server_environment',
        'server_environment_files',
    ],
    'data': [
        "data/s3_import_data.xml",
        "views/journal_view.xml"
    ],
    'external_dependencies': {
        'python': ['boto'],
    },
    'installable': True,
}
