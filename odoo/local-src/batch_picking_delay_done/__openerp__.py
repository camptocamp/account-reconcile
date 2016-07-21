# -*- coding: utf-8 -*-

{
    'name': 'Batch Picking Delay Done',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'maintainer': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'depends': [
        'stock_batch_picking',  # stock-logistics-workflow
    ],
    'description': """
Batch Picking Delay Done
===========================

Adds a button on the Batch Picking allowing to set the batch to done,
later. A cron will process them so the user is not blocked.
Add a state on the batch picking 'Delayed Done'.
""",
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/cron.xml',
        'views/stock_batch_picking.xml',
        'wizard/batch_picking_delayed_done_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
