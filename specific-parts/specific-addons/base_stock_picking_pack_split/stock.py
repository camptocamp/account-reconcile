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


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _split_into_quantity(self, cr, uid, move, quantity, context=None):
        """ Optimized version of the wizard stock.split.into

        Contrary to the wizard, it returns the id of the new move.
        Also, it does not call move.setlast_tracking() if it is not
        necessary.
        """
        track_obj = self.pool['stock.tracking']
        if quantity > move.product_qty:
            raise orm.except_orm(
                _('Error'),
                _('Total quantity after split exceeds the '
                  'quantity to split for this product: '
                  '"%s" (id: %d).') % (move.product_id.name,
                                       move.product_id.id))
        quantity_rest = move.product_qty - quantity
        if quantity > 0:
            if not move.tracking_id:
                move.setlast_tracking()
            move.write({'product_qty': quantity,
                        'product_uos_qty': quantity,
                        'product_uos': move.product_uom.id,
                        })

        if quantity_rest > 0:
            tracking_id = track_obj.create(cr, uid, {}, context=context)
            if quantity == 0.0:
                move.write({'tracking_id': tracking_id})
            else:
                default_val = {
                    'product_qty': quantity_rest,
                    'product_uos_qty': quantity_rest,
                    'tracking_id': tracking_id,
                    'state': move.state,
                    'product_uos': move.product_uom.id
                }
                current_move_id = self.copy(cr, uid, move.id,
                                            default_val, context=context)
                return current_move_id


    def setlast_tracking(self, cr, uid, ids, context=None):
        """ Optimized version of setlast_tracking

        Can be removed once a PR is merged:
            https://github.com/odoo/odoo/pull/2448
            https://github.com/OCA/OCB/pull/49

        """
        tracking_obj = self.pool.get('stock.tracking')
        assert len(ids) == 1, "1 ID expected, got %s" % (ids, )
        move = self.browse(cr, uid, ids[0], context=context)
        picking_id = move.picking_id.id
        if picking_id:
            move_ids = self.search(cr, uid,
                                   [('picking_id', '=', picking_id),
                                    ('tracking_id', '!=', False)],
                                   limit=1,
                                   order='tracking_id desc',
                                   context=context)
            if move_ids:
                tracking_move = self.browse(cr, uid, move_ids[0],
                                            context=context)
                tracking_id = tracking_move.tracking_id.id
            else:
                tracking_id = tracking_obj.create(cr, uid, {}, context=context)
            self.write(cr, uid, move.id, {'tracking_id': tracking_id})
        return True


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def prepare_packs(self, cr, uid, ids, max_qty=1, context=None):
        """ Fill packs with products

        We consider that all product of the picking have the same size.

        A pack will be filled by a type of product, if some space is left
        then we try to fill it with the products of the next picking line
        and so on...

        """
        move_obj = self.pool.get('stock.move')
        for pick_id in ids:
            # Benchmarks measured that browsing them one by one was
            # way more fast. The browse in the for loop was consuming
            # an exponential time, the more pickings there was,
            # the more it took time in an exponential manner
            pick = self.browse(cr, uid, pick_id, context=context)
            if pick.state in ('cancel', 'done'):
                continue

            # copy this list of move
            moves_to_split = [m for m in pick.move_lines]

            current_pack = None
            while moves_to_split:
                move = moves_to_split.pop()
                # Set a tracking_id on the move, the value is the last
                # one of another move of the same picking, or a new one
                # if the last picking hadn't a tracking
                move.setlast_tracking()
                # ensure written change is readable
                move.refresh()

                current_pack = move.tracking_id
                pack_qty = sum(m.product_qty for m in current_pack.move_ids)
                if pack_qty == max_qty:
                    current_pack = None
                    continue

                if pack_qty > max_qty:
                    qty_to_pack = move.product_qty - (pack_qty - max_qty)
                    split = move_obj._split_into_quantity
                    new_move_id = split(cr, uid, move, qty_to_pack,
                                        context=context)

                    if new_move_id:
                        new_move = move_obj.browse(cr, uid, new_move_id,
                                                   context=context)
                        moves_to_split.append(new_move)
                    else:
                        # If qty to split == move qty (qty_to_pack == 0),
                        # the move was simply given a new tracking_id.
                        # We add it to check it again.
                        moves_to_split.append(move)
        return True
