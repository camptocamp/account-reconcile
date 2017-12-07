# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'Sale Automatic Workflow Split',
 'version': '9.0.1.0.0',
 'category': 'Sales Management',
 'description': """

Split the automatic workflows in several independent crons (no card, following
performance issues on production). Allow different intervals. Validating
invoices takes a lot of time for instance but does not need to be done very
fast. Confirming sales orders has to wait on validation on invoices, but we
want this operation to be fast.

""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'https://www.camptocamp.com/',
 'depends': ['sale_automatic_workflow_payment_mode',
             'specific_fct',  # for admin_ch user
             ],
 'data': ['data/ir_cron.xml',
          ],
 'test': [],
 'installable': True,
 }
