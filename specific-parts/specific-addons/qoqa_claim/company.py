# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2016 Camptocamp SA
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


class ResCompany(orm.Model):
    _inherit = "res.company"

    _columns = {
        'unclaimed_initial_categ_id': fields.many2one(
            'crm.case.categ',
            'Default category for new unclaimed packages'),
        'unclaimed_first_reminder_categ_id': fields.many2one(
            'crm.case.categ',
            'Default category for unclaimed packages after first reminder'),
        'unclaimed_second_reminder_categ_id': fields.many2one(
            'crm.case.categ',
            'Default category for unclaimed packages after second reminder'),
        'unclaimed_final_categ_id': fields.many2one(
            'crm.case.categ',
            'Default category for sent back unclaimed packages'),
        'unclaimed_stock_journal_id': fields.many2one(
            'stock.journal',
            'Default stock journal for unclaimed packages'),
    }
