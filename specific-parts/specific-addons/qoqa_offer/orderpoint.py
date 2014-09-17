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

from openerp.osv import orm
from openerp import netsvc


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
        procurement_obj = self.pool['procurement.order']
        _prepare_op = procurement_obj._prepare_orderpoint_procurement
        wf_service = netsvc.LocalService("workflow")

        generated_proc_ids = []
        for op in self.browse(cr, uid, ids, context=context):
            prods = procurement_obj._product_virtual_get(cr, uid, op)
            if prods is None:
                continue
            if prods < op.product_min_qty:
                qty = max(op.product_min_qty, op.product_max_qty) - prods

                reste = qty % op.qty_multiple
                if reste > 0:
                    qty += op.qty_multiple - reste

                if qty <= 0:
                    continue

                if op.product_id.type not in ('consu'):
                    if op.procurement_draft_ids:
                        # Check draft procurement related to this
                        # order point
                        pro_ids = [x.id for x in op.procurement_draft_ids]
                        procure_datas = procurement_obj.read(
                            cr, uid, pro_ids,
                            ['id', 'product_qty'], context=context)
                        to_generate = qty
                        for proc_data in procure_datas:
                            if to_generate >= proc_data['product_qty']:
                                wf_service.trg_validate(
                                    uid, 'procurement.order',
                                    proc_data['id'], 'button_confirm', cr)
                                procurement_obj.write(cr, uid,
                                                      [proc_data['id']],
                                                      {'origin': op.name},
                                                      context=context)
                                to_generate -= proc_data['product_qty']
                            if not to_generate:
                                break
                        qty = to_generate

                if qty:
                    vals = _prepare_op(cr, uid, op, qty, context=context)
                    proc_id = procurement_obj.create(cr, uid, vals,
                                                     context=context)
                    wf_service.trg_validate(uid, 'procurement.order',
                                            proc_id, 'button_confirm', cr)
                    wf_service.trg_validate(uid, 'procurement.order',
                                            proc_id, 'button_check', cr)
                    self.write(cr, uid, [op.id],
                               {'procurement_id': proc_id},
                               context=context)
                    generated_proc_ids.append(proc_id)
        return generated_proc_ids
