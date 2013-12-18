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
from openerp.osv import orm


class stock_tracking(orm.Model):
    _inherit = 'stock.tracking'

    def get_total_qty(self, cr, uid, ids, context=None):
        res = dict.fromkeys(ids, False)
        for pack in self.browse(cr, uid, ids, context=context):
            res[pack.id] = sum(m.product_qty for m in pack.move_ids)
        return res


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def compute_qty_to_pack(self, cr, uid, ids, pack_qty, max_qty, context=None):
        res = dict.fromkeys(ids, False)
        for move in self.browse(cr, uid, ids, context=context):
            qty_to_unpack = pack_qty - max_qty
            res[move.id] = move.product_qty - qty_to_unpack
        return res


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def prepare_packs(self, cr, uid, ids, max_qty=1, context=None):
        """ Fill packs with products

        We consider that all product of the picking have the same size.

        A pack will be filled by a type of product, if some space is left
        then we try to fill it with the products of the next picking line
        and so on...

        """
        if context is None:
            context = {}
        split_wizard_obj = self.pool.get('stock.split.into')
        move_obj = self.pool.get('stock.move')

        for pick in self.browse(cr, uid, ids, context=context):

            # We register moves to find which move has been added
            known_move_ids = [m.id for m in pick.move_lines]
            # copy this list of move
            moves_to_split = [m for m in pick.move_lines]

            current_pack = None
            while moves_to_split:
                move = moves_to_split.pop()
                move.setlast_tracking()

                # ensure written change is readable
                move.refresh()

                current_pack = move.tracking_id

                pack_qty = current_pack.get_total_qty()[current_pack.id]
                if pack_qty == max_qty:
                    current_pack = None
                    continue

                if pack_qty > max_qty:
                    qty_to_pack = move.compute_qty_to_pack(
                        pack_qty, max_qty)[move.id]
                    wiz_data = {'quantity': qty_to_pack}
                    wiz_ctx = context.copy()
                    wiz_ctx.update(active_ids=[move.id],
                                   res_model='stock.move')
                    wiz_id = split_wizard_obj.create(cr, uid, wiz_data,
                                                     context=context)
                    split_wizard_obj.split(cr, uid, [wiz_id], context=wiz_ctx)

                    # ensure written change is readable
                    move.refresh()

                    # Find created move with residual products using search as
                    # we can't use pick.move_lines. Because browse record isn't
                    # refreshed
                    new_move_ids = move_obj.search(
                        cr, uid,
                        [('picking_id', '=', pick.id),
                         ('id', 'not in', known_move_ids)],
                        context=context)

                    if new_move_ids:
                        # split function must have created only 1 move
                        assert len(new_move_ids) == 1
                        known_move_ids.append(new_move_ids[0])
                        new_move = move_obj.browse(cr, uid, new_move_ids,
                                                   context=context)[0]
                        moves_to_split.append(new_move)
                    else:
                        # If qty to split == move qty (qty_to_pack == 0),
                        # the move was simply given a new tracking_id.
                        # We add it to check it again.
                        moves_to_split.append(move)
