# -*- coding: utf-8 -*-
# © 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'Account Mass Reconcile as Jobs',
 'version': '9.0.1.0.0',
 'category': 'Accounting',
 'depends': ['connector',
             'account_mass_reconcile',
             'account_mass_reconcile_transaction_ref',
             'account_mass_reconcile_ref_deep_search',
             ],
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'https://www.camptocamp.com',
 'description': """
Account Mass Reconcile as Jobs
==============================

Modify the mass reconcile to do only the search (create the groups to
reconcile), but process them asynchronously as jobs.

It could be a generic one but, especially in 9.0, it's a bit hackish and there
are some drawbacks:

 * we need to put some code in every inherited reconcile method, due to a bug
   before Odoo 10.0 (inherit models don't get changes done on a base model
   after an inherit)
 * the behavior is a bit weird as the design of the addon was really thought
   for a synchronous workflow (the history shows the last reconciled lines,
   which will no longer work)

The feature can be disabled by setting the ir.config_parameter
"account.mass.reconcile.as.job" to False.

""",
 'data': [
          'data/ir_config_parameter.xml',
          ],
 'installable': True,
 'application': False,
 }
