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


class picking_dispatch(orm.Model):
    _inherit = 'picking.dispatch'

    def action_assign_moves(self, cr, uid, ids, context=None):
        for dispatch_id in ids:
            move_obj = self.pool['stock.move']
            move_ids = move_obj.search(cr, uid,
                                       [('dispatch_id', '=', dispatch_id)],
                                       context=context)
            move_obj.action_assign(cr, uid, move_ids)
        return True
