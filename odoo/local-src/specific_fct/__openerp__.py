# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'QoQa Specific',
    'version': '9.0.1.0.0',
    'category': 'Others',
    'depends': [
        'account_reports',
        'account_analytic_required',
        'account_mass_reconcile',
        'account_move_base_import',
        'account_payment_mode',
        'auth_totp',
        'hr_holidays',
        'sale',
        'stock_batch_picking',
        'stock_picking_mass_assign',
        'product',
        'purchase',
        'purchase_analytic_global',
        'purchase_order_variant_mgmt',
        'delivery_carrier_label_postlogistics_shop_logo',
        'qoqa_offer',
        'base_delivery_carrier_label',
        'delivery_carrier_label_batch',
        'base_transaction_id',
        'connector_qoqa',
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_invoice_view.xml',
        'views/account_tax_view.xml',
        'views/auth_totp_view.xml',
        'views/hr_holidays_view.xml',
        'views/partner_view.xml',
        'views/account_payment_mode_view.xml',
        'views/stock_batch_picking_view.xml',
        'views/product_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/account_move_line_view.xml',
        'wizard/account_invoice_refund_view.xml',
        'data/user_data.xml',
        'data/cron_data.xml',
        'data/mail_data.xml',
        'data/product_category.xml',
        'data/delete_translation.sql',
    ],
    'installable': True,
    'application': True,
}
