# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'Speedy Views',
 'version': '9.1.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Misc',
 'depends': ['account',
             'sale_stock',
             'purchase',
             'crm_claim_rma',
             'stock_batch_picking',
             'specific_fct',
             'account_move_base_import',
             'base_transaction_id',
             ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'views/account_views.xml',
     'views/sale_views.xml',
  ],
 'installable': True,
 }
