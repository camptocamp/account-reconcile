# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm, fields


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'validation_agreement': fields.boolean('Agreement to validation'),
    }

    def action_move_create(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for invoice in self.browse(cr, uid, ids, context=context):
            for line in invoice.invoice_line:
                # ensure that there is no analytic accounts on lines
                # when the policy is never
                if (line.account_id.user_type.analytic_policy == 'never' and
                        line.account_analytic_id):
                    line.write({'account_analytic_id': False})
        return super(account_invoice, self).action_move_create(
            cr, uid, ids, context=context)

    def button_validate_agreement(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,
                   {'validation_agreement': True},
                   context=context)
        return True
