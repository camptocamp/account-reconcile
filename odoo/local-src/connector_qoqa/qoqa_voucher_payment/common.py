# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class QoqaVoucherPayment(models.Model):
    _name = 'qoqa.voucher.payment'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move': 'openerp_id'}
    _description = 'QoQa Voucher Payment'

    openerp_id = fields.Many2one(comodel_name='account.move',
                                 string='Move',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')
    qoqa_order_id = fields.Many2one(
        comodel_name='qoqa.sale.order',
        string='QoQa Sale Order',
        ondelete='restrict',
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    qoqa_voucher_payment_bind_ids = fields.One2many(
        comodel_name='qoqa.voucher.payment',
        inverse_name='openerp_id',
        copy=False,
        string='QBindings',
        context={'active_test': False},
    )
