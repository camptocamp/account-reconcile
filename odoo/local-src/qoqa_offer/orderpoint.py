# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

# flake8: noqa
# this is a raw copy with slight adaptations of
# odoo/src/addons/stock/procurement.py ->
# procurement_order._procure_orderpoint_confirm

from openerp.osv import orm
from openerp.tools import float_compare, float_round


class stock_warehouse_orderpoint(orm.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def procure_orderpoint_confirm(self, cr, uid, ids, context=None):
        """
        Create procurement based on Orderpoint.

        Based on procurement_order._procure_orderpoint_confirm but allow
        to work on a selection. Do not allow to work with a new cursor nor
        to run the automatic orderpoints.

        Returns the list of generated procurements.
        """
        if context is None:
            context = {}
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        procurement_obj = self.pool.get('procurement.order')
        product_obj = self.pool.get('product.product')

        _prepare_op = procurement_obj._prepare_orderpoint_procurement

        product_dict = {}
        ops_dict = {}
        tot_procs = []
        ops = self.browse(cr, uid, ids, context=context)

        #Calculate groups that can be executed together
        for op in ops:
            key = (op.location_id.id,)
            if not product_dict.get(key):
                product_dict[key] = [op.product_id]
                ops_dict[key] = [op]
            else:
                product_dict[key] += [op.product_id]
                ops_dict[key] += [op]

        for key in product_dict.keys():
            ctx = context.copy()
            ctx.update({'location': ops_dict[key][0].location_id.id})
            prod_qty = product_obj._product_available(cr, uid, [x.id for x in product_dict[key]],
                                                      context=ctx)
            subtract_qty = orderpoint_obj.subtract_procurements_from_orderpoints(cr, uid, [x.id for x in ops_dict[key]], context=context)
            for op in ops_dict[key]:
                prods = prod_qty[op.product_id.id]['virtual_available']
                if prods is None:
                    continue
                if float_compare(prods, op.product_min_qty, precision_rounding=op.product_uom.rounding) <= 0:
                    qty = max(op.product_min_qty, op.product_max_qty) - prods
                    reste = op.qty_multiple > 0 and qty % op.qty_multiple or 0.0
                    if float_compare(reste, 0.0, precision_rounding=op.product_uom.rounding) > 0:
                        qty += op.qty_multiple - reste

                    if float_compare(qty, 0.0, precision_rounding=op.product_uom.rounding) < 0:
                        continue

                    qty -= subtract_qty[op.id]

                    qty_rounded = float_round(qty, precision_rounding=op.product_uom.rounding)
                    if qty_rounded > 0:
                        proc_id = procurement_obj.create(cr, uid,
                                                         _prepare_op(cr, uid, op, qty_rounded, context=context),
                                                         context=dict(context, procurement_autorun_defer=True))
                        tot_procs.append(proc_id)

            tot_procs.reverse()
            procurement_obj.run(cr, uid, tot_procs, context=context)

        return tot_procs
