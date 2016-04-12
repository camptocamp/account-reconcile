# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

On the QoQa backend are generated vouchers and promo.
They are used a bit like credit notes / gift cards.

When used in sales orders, they are imported like payments for vouchers
and as negative lines for promos.

We have to create move lines for the issuance of theses goods, as they
are created on the QoQa backend and should be accounted.

From a technical viewpoint, we have 1 API entry point:
``api/v1/promo_accounting``.

Both promo and vouchers are mixed. So we have 1 virtual model on QoQa,
but we split them in 2 models in OpenERP.

Each line returned by the API is mapped with an account.move.line but
also has a reference to either a 'voucher_id' either a 'promo_id'.

So we we also bind the voucher_id and promo_id with the account.move

"""

from openerp import models, fields, api

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaAccountingIssuance(models.Model):
    _name = 'qoqa.accounting.issuance'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move': 'openerp_id'}
    _description = 'QoQa Accounting Issuance'

    openerp_id = fields.Many2one(comodel_name='account.move',
                                 string='Journal Entry',
                                 required=True,
                                 index=True,
                                 ondelete='cascade')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')
    # either promo, either voucher
    voucher_id = fields.Float(string='QoQa Voucher ID')
    promo_id = fields.Float(string='QoQa Promo ID')
    qoqa_promo_line_ids = fields.One2many(
        comodel_name='qoqa.promo.issuance.line',
        inverse_name='qoqa_issuance_id',
        string='QoQa Promo Issuance Line',
    )
    qoqa_voucher_line_ids = fields.One2many(
        comodel_name='qoqa.voucher.issuance.line',
        inverse_name='qoqa_issuance_id',
        string='QoQa Voucher Issuance Line',
    )

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A promo issuance can be exported only once on the same backend"),
    ]


class QoqaPromoIssuanceLine(models.Model):
    _name = 'qoqa.promo.issuance.line'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move.line': 'openerp_id'}
    _description = 'QoQa Promo Issuance'

    openerp_id = fields.Many2one('account.move.line',
                                 string='Journal Item',
                                 required=True,
                                 index=True,
                                 ondelete='cascade')
    created_at = fields.Datetime('Created At (on QoQa)')
    updated_at = fields.Datetime('Updated At (on QoQa)')
    qoqa_issuance_id = fields.Many2one(comodel_name='qoqa.accounting.issuance',
                                       string='QoQa Accounting Issuance',
                                       required=True,
                                       readonly=True,
                                       ondelete='cascade',
                                       index=True)

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A promo issuance line can be exported only once on "
         "the same backend"),
    ]

    @api.model
    def create(self, vals):
        # rebind lines with the move as they are created
        # through _inherits
        binding_id = vals['qoqa_issuance_id']
        issuance_model = self.env['qoqa.accounting.issuance']
        binding = issuance_model.browse(binding_id)
        issuance = binding.openerp_id
        vals['move_id'] = issuance.id
        return super(QoqaPromoIssuanceLine, self).create(vals)


class QoqaVoucherIssuanceLine(models.Model):
    _name = 'qoqa.voucher.issuance.line'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move.line': 'openerp_id'}
    _description = 'QoQa Voucher Issuance Line'

    openerp_id = fields.Many2one(comodel_name='account.move.line',
                                 string='Journal Item',
                                 required=True,
                                 index=True,
                                 ondelete='cascade')
    created_at = fields.Datetime('Created At (on QoQa)')
    updated_at = fields.Datetime('Updated At (on QoQa)')
    qoqa_issuance_id = fields.Many2one(comodel_name='qoqa.accounting.issuance',
                                       string='QoQa Accounting Issuance',
                                       required=True,
                                       readonly=True,
                                       ondelete='cascade',
                                       index=True)

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A voucher issuance line can be exported only once "
         "on the same backend"),
    ]

    @api.model
    def create(self, vals):
        # rebind lines with the move as they are created
        # through _inherits
        binding_id = vals['qoqa_issuance_id']
        issuance_model = self.env['qoqa.accounting.issuance']
        binding = issuance_model.read(binding_id)
        issuance = binding.openerp_id
        vals['move_id'] = issuance.id
        return super(QoqaVoucherIssuanceLine, self).create(vals)


class AccountMove(models.Model):
    _inherit = 'account.move'

    qoqa_accounting_issuance_bind_ids = fields.One2many(
        comodel_name='qoqa.accounting.issuance',
        inverse_name='openerp_id',
        string='QoQa Accounting Issuances',
        copy=False,
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    qoqa_promo_issuance_line_bind_ids = fields.One2many(
        comodel_name='qoqa.promo.issuance.line',
        inverse_name='openerp_id',
        string='QoQa Promo Issuances Line',
        copy=False,
    )
    qoqa_voucher_issuance_line_bind_ids = fields.One2many(
        comodel_name='qoqa.voucher.issuance.line',
        inverse_name='openerp_id',
        string='QoQa Voucher Issuances Line',
        copy=False,
    )

    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        # fix a bug when we create a move line from an inherits
        if 'journal_id' in context and not context['journal_id']:
            del context['journal_id']
        if 'period_id' in context and not context['period_id']:
            del context['period_id']
        self_c = self.with_context(context)
        return super(AccountMoveLine, self_c).create(vals)


@qoqa
class QoQaAccountingIssuanceAdapter(QoQaAdapter):
    _model_name = 'qoqa.accounting.issuance',
    _endpoint = 'promo_accounting_group'
