# -*- coding: utf-8 -*-

{
    'name': 'Batch Picking - Automatic Grouping',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'maintainer': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Stock Logistics',
    'complexity': "normal",
    'depends': [
        'stock_batch_picking',
    ],
    'description': """
Batch Picking - Automatic Grouping
=====================================

Allows to create batch picking based on a list of Delivery Orders.

""",
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/batch_picking_report.xml',
        'views/stock_picking_view.xml',
        'wizard/batch_group_view.xml',
        'wizard/batch_picking_warnings.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
