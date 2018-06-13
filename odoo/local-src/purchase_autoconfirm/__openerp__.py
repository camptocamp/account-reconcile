# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'QoQa Purchase Autoconfirm',
    'version': '9.0.1.0.0',
    'category': 'Others',
    'depends': [
        'account_payment_mode',
        'purchase',
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/po_cron.xml',
    ],
}
