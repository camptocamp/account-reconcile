# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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

from openerp.osv import orm, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_promo_issuance(orm.Model):
    _name = 'qoqa.promo.issuance'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move': 'openerp_id'}
    _description = 'QoQa Promo Issuance'

    _columns = {
        'openerp_id': fields.many2one('account.move',
                                      string='Journal Entry',
                                      required=True,
                                      ondelete='cascade'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A promo issuance with the same ID on QoQa already exists")
    ]


class qoqa_promo_issuance_line(orm.Model):
    _name = 'qoqa.promo.issuance.line'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move.line': 'openerp_id'}
    _description = 'QoQa Promo Issuance'

    _columns = {
        'openerp_id': fields.many2one('account.move.line',
                                      string='Journal Item',
                                      required=True,
                                      ondelete='cascade'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A promo issuance line with the same ID on QoQa already exists")
    ]


class qoqa_voucher_issuance(orm.Model):
    _name = 'qoqa.voucher.issuance'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move': 'openerp_id'}
    _description = 'QoQa Voucher Issuance'

    _columns = {
        'openerp_id': fields.many2one('account.move',
                                      string='Journal Entry',
                                      required=True,
                                      ondelete='cascade'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A voucher issuance with the same ID on QoQa already exists")
    ]


class qoqa_voucher_issuance_line(orm.Model):
    _name = 'qoqa.voucher.issuance.line'
    _inherit = 'qoqa.binding'
    _inherits = {'account.move.line': 'openerp_id'}
    _description = 'QoQa Voucher Issuance Line'

    _columns = {
        'openerp_id': fields.many2one('account.move.line',
                                      string='Journal Item',
                                      required=True,
                                      ondelete='cascade'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A voucher issuance line with the same ID on QoQa already exists")
    ]


class account_move(orm.Model):
    _inherit = 'account.move'

    _columns = {
        'qoqa_promo_issuance_bind_ids': fields.one2many(
            'qoqa.promo.issuance',
            'openerp_id',
            string='QoQa Promo Issuances'),
        'qoqa_voucher_issuance_bind_ids': fields.one2many(
            'qoqa.voucher.issuance',
            'openerp_id',
            string='QoQa Voucher Issuances'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_promo_issuance_bind_ids': False,
            'qoqa_voucher_issuance_bind_ids': False,
        })
        return super(account_move, self
                     ).copy_data(cr, uid, id, default=default, context=context)




class account_move_line(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        'qoqa_promo_issuance_line_bind_ids': fields.one2many(
            'qoqa.promo.issuance.line',
            'openerp_id',
            string='QoQa Promo Issuances Line'),
        'qoqa_voucher_issuance_line_bind_ids': fields.one2many(
            'qoqa.voucher.issuance.line',
            'openerp_id',
            string='QoQa Voucher Issuances Line'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_promo_issuance_line_bind_ids': False,
            'qoqa_voucher_issuance_line_bind_ids': False,
        })
        return super(account_move_line, self
                     ).copy_data(cr, uid, id, default=default, context=context)

    def create(self, cr, uid, vals, context=None, check=True):
        if context is None:
            context = {}
        else:
            # fix a bug when we create a move line from an inherits
            if 'journal_id' in context and not context['journal_id']:
                del context['journal_id']
            if 'period_id' in context and not context['period_id']:
                del context['period_id']
        return super(account_move_line, self
                     ).create(cr, uid, vals, context=context, check=check)


@qoqa
class qoqa_promo_issuance(QoQaAdapter):
    _model_name = ['qoqa.promo.issuance.line',
                   'qoqa.voucher.issuance.line',
                   ]
    _endpoint = 'promo_accounting'
