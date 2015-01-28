# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville
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


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    def _check_currency_amount(self, cr, uid, ids, context=None):
        # Deactivation of constraint:
        # please see for more details the issue
        # https://github.com/OCA/account-financial-tools/issues/135
        # more precisely the case 1
        return True

    _constraints = [
                    (_check_currency_amount,
                    "The amount expressed in the secondary currency must be positive "
                    "when journal item are debit and negatif when journal item are "
                    "credit.",
                     ['amount_currency']
            ),
        ]
