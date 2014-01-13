# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
from openerp.osv import orm, fields


class stock_picking(orm.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.

    """
    _inherit = "stock.picking"

    def _get_number_of_products(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            number_of_products = 0
            for line in picking.move_lines:
                number_of_products += line.product_qty
            result[picking.id] = number_of_products
        return result

    def _get_picking(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('stock.move')
        for line in move_obj.browse(cr, uid, ids, context=context):
            result.add(line.picking_id.id)
        return list(result)

    _columns = {
        'number_of_products': fields.function(
            _get_number_of_products, method=True,
            type='integer', string='Number of products',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            }),
    }

class stock_picking_in(orm.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.

    """
    _inherit = "stock.picking.in"

    def _get_number_of_products(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            number_of_products = 0
            for line in picking.move_lines:
                number_of_products += line.product_qty
            result[picking.id] = number_of_products
        return result

    def _get_picking(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('stock.move')
        for line in move_obj.browse(cr, uid, ids, context=context):
            result.add(line.picking_id.id)
        return list(result)

    _columns = {
        'number_of_products': fields.function(
            _get_number_of_products, method=True,
            type='integer', string='Number of products',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            }),
    }

class stock_picking_out(orm.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.

    """
    _inherit = "stock.picking.out"

    def _get_number_of_products(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            number_of_products = 0
            for line in picking.move_lines:
                number_of_products += line.product_qty
            result[picking.id] = number_of_products
        return result

    def _get_picking(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('stock.move')
        for line in move_obj.browse(cr, uid, ids, context=context):
            result.add(line.picking_id.id)
        return list(result)

    _columns = {
        'number_of_products': fields.function(
            _get_number_of_products, method=True,
            type='integer', string='Number of products',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            }),
    }
