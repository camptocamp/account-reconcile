# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaDiscountAccounting(models.Model):
    _name = 'qoqa.discount.accounting'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move': 'openerp_id'}
    _description = 'QoQa Discount Accounting'

    openerp_id = fields.Many2one(comodel_name='account.move',
                                 string='Journal Entry',
                                 required=True,
                                 index=True,
                                 ondelete='cascade')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')
    qoqa_discount_accounting_line_ids = fields.One2many(
        comodel_name='qoqa.discount.accounting.line',
        inverse_name='qoqa_discount_accounting_id',
        string='QoQa Discount Accounting Line',
    )
    discount_type = fields.Selection(
        # voucher is now deprecated but kept for the history
        selection=[('promo', 'Promo'), ('voucher', 'Voucher')],
        string='Discount Type',
    )

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "This move line is already linked with a QoQa discount accounting."),
    ]


class QoqaDiscountAccountingLine(models.Model):
    _name = 'qoqa.discount.accounting.line'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move.line': 'openerp_id'}
    _description = 'QoQa Discount Accounting Line'

    openerp_id = fields.Many2one('account.move.line',
                                 string='Journal Item',
                                 required=True,
                                 index=True,
                                 ondelete='cascade')
    created_at = fields.Datetime('Created At (on QoQa)')
    updated_at = fields.Datetime('Updated At (on QoQa)')
    qoqa_discount_accounting_id = fields.Many2one(
        comodel_name='qoqa.discount.accounting',
        string='QoQa Discount Accounting',
        required=True,
        readonly=True,
        ondelete='cascade',
        index=True,
    )

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A discount accounting line can be exported only once on "
         "the same backend"),
    ]

    @api.model
    def create(self, vals):
        # rebind lines with the move as they are created
        # through _inherits
        binding_id = vals['qoqa_discount_accounting_id']
        discount_model = self.env['qoqa.discount.accounting']
        binding = discount_model.browse(binding_id)
        accounting_group = binding.openerp_id
        vals['move_id'] = accounting_group.id
        return super(QoqaDiscountAccountingLine, self).create(vals)


class AccountMove(models.Model):
    _inherit = 'account.move'

    qoqa_discount_accounting_bind_ids = fields.One2many(
        comodel_name='qoqa.discount.accounting',
        inverse_name='openerp_id',
        string='QoQa Discount Accounting',
        copy=False,
        context={'active_test': False},
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    qoqa_discount_accounting_line_bind_ids = fields.One2many(
        comodel_name='qoqa.discount.accounting.line',
        inverse_name='openerp_id',
        string='QoQa Discount Accounting Line',
        copy=False,
        context={'active_test': False},
    )


@qoqa
class QoQaDiscountAccountingAdapter(QoQaAdapter):
    _model_name = 'qoqa.discount.accounting',
    _endpoint = 'admin/discount_accountings'
    _resource = 'discount_accounting'
