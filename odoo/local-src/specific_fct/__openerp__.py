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
        'hr_holidays',
        'sale',
        'stock_batch_picking',
        'stock_picking_mass_assign',
        'product',
        'purchase',
        'purchase_analytic_global',
        'delivery_carrier_label_postlogistics_shop_logo',
        'qoqa_offer',
        'delivery_carrier_label_batch',
        'base_transaction_id',
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_invoice_view.xml',
        'views/hr_holidays_view.xml',
        'views/partner_view.xml',
        'views/account_payment_mode_view.xml',
        'views/stock_batch_picking_view.xml',
        'views/product_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'wizard/account_invoice_refund_view.xml',
        'data/product_category.xml',
    ],
    'installable': True,
    'application': True,
}
