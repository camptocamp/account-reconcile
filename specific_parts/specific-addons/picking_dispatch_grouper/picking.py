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


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _get_all_in_dispatch(self, cr, uid, ids, name, args, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            in_dispatch = True
            for move in picking.move_lines:
                if not move.dispatch_id:
                    in_dispatch = False
            res[picking.id] = in_dispatch
        return res

    def _search_all_in_dispatch(self, cr, uid, obj, name, args, context):
        res = []
        for _field, operator, value in args:
            assert operator in ('=', '!=', '<>') and value in (True, False), \
                'Operation not supported: %s %s' % (operator, value)
            if (operator == '=' and value is True or
                    operator in ('<>', '!=') and value is False):
                search_operator = 'not in'
            else:
                search_operator = 'in'
            query = ("SELECT p.id FROM stock_picking p "
                     "INNER JOIN stock_move m "
                     "ON m.picking_id = p.id "
                     "WHERE m.dispatch_id IS NULL "
                     "GROUP BY p.id ")
            cr.execute(query)
            res_ids = [row[0] for row in cr.fetchall()]
            res.append(('id', search_operator, res_ids))
        return res

    _columns = {
        'all_in_dispatch': fields.function(
            _get_all_in_dispatch,
            fnct_search=_search_all_in_dispatch,
            type='boolean',
            string='All In Dispatch')
    }


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    def _get_all_in_dispatch(self, cr, uid, ids, name, args, context=None):
        return super(stock_picking_out, self).\
            _get_all_in_dispatch(cr, uid, ids, name, args, context=context)

    def _search_all_in_dispatch(self, cr, uid, obj, name, args, context):
        return super(stock_picking_out, self).\
            _search_all_in_dispatch(cr, uid, obj, name, args, context=context)

    _columns = {
        'all_in_dispatch': fields.function(
            _get_all_in_dispatch,
            fnct_search=_search_all_in_dispatch,
            type='boolean',
            string='All In Dispatch')
    }


# TODO activate when the
# https://bugs.launchpad.net/ocb-addons/+bug/1281558
# bug is corrected, meanwhile it would prevent to duplicate a picking

# class stock_move(orm.Model):
#     _inherit = 'stock.move'

#     def _check_tracking(self, cr, uid, ids, context=None):
#         for move in self.browse(cr, uid, ids, context=context):
#             if not move.tracking_id:
#                 continue
#             picking = move.picking_id
#             if any(tm.picking_id != picking for
#                    tm in move.tracking_id.move_ids):
#                 return False
#         return True

#     _constraints = [
#         (_check_tracking,
#          'The tracking cannot be shared accross '
#          'different Delivery Orders / Shipments.',
#          ['tracking_id']),
#     ]
