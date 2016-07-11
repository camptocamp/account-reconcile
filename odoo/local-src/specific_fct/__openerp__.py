# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'QoQa Specific',
    'version': '9.0.1.0.0',
    'category': 'Others',
    'depends': [
        # TODO: waiting for https://github.com/OCA/account-analytic/pull/59
        # 'account_analytic_required',
        'sale',
        'stock_picking_dispatch',
        'stock_picking_mass_assign',
        'product',
        'purchase',
        'purchase_analytic_global',
        'delivery_carrier_label_postlogistics_shop_logo',
        'qoqa_offer',
        # TODO: A plus!
        # 'account_payment',
        # TODO: Waiting for connector
        # 'connector_qoqa',
        # TODO: waiting for http://jira.qoqa.com/browse/MIGO-127
        # 'delivery_carrier_label_dispatch',
        'base_transaction_id',
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'description': """
QoQa Specific
=============

Local customizations for QoQa.

Product:

set cost_method default to average

Stock.move:

Overwrite of do_partial to keep tracking id of unprocessed packs

Picking dispatch:
Hide the cancel button action to avoid human mistakes
""",
    'css': [
        'static/src/css/base.css',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # TODO
        # 'account_invoice_view.xml',
        'views/hr_holidays_view.xml',
        'views/partner_view.xml',
        # TODO
        # 'views/payment_view.xml',
        # TODO: Waiting for connector
        # 'views/payment_method_view.xml',
        'views/picking_dispatch_view.xml',
        'views/product_view.xml',
        # TODO
        # 'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'wizard/account_invoice_refund_view.xml',
    ],
    'installable': True,
    'application': True,
}
