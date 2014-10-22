# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
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
from openerp.osv import orm


class AccountStatementProfil(orm.Model):
    _inherit = "account.statement.profile"

    # Due to commit
    # https://github.com/OCA/bank-statement-reconcile/commit/70226284b
    # balance_start is set in the imported bank statement. QoQa does not
    # want it, so we redefine it to False.
    def prepare_statement_vals(self, cr, uid, profile_id, result_row_list,
                               parser, context=None):
        vals = super(AccountStatementProfil, self).prepare_statement_vals(
            cr, uid, profile_id, result_row_list, parser, context=context
        )
        vals['balance_start'] = False
        return vals
