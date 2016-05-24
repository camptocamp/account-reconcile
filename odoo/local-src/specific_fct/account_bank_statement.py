# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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


class AccountBankStatement(orm.Model):
    _inherit = "account.bank.statement"

    def button_journal_entries(self, cr, uid, ids, context=None):
        # Remove existing groupbys
        # (to avoid non-existing fields on move lines)
        ctx = (context or {}).copy()
        if 'group_by' in ctx:
            del ctx['group_by']
        return super(AccountBankStatement, self).button_journal_entries(
            cr, uid, ids, context=ctx
        )
