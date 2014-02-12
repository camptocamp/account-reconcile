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

from itertools import islice
from openerp.osv import orm, fields


class picking_dispatch_grouper(orm.TransientModel):
    _name = 'picking.dispatch.grouper'
    _description = 'Picking Dispatch Grouper'

    _columns = {
        'max_pack': fields.integer(
            'Max number of packs in a dispatch',
            help='Leave 0 to set no limit'),
        'only_product_ids': fields.many2many(
            'product.product',
            string='Filter on products',
            help='Dispatchs will be created only if the '
                 'pack contains at least one of these products.\n'
                 'No filter is applied when no product is selected. '),
        'group_by_set': fields.boolean(
            'Group By Set',
            help='Packs with similar content will be grouped in '
                 'the same dispatch'),
        'group_leftovers': fields.boolean(
            'Put the leftovers in the same dispatch',
            help='When packs do not fall in a group, they will be '
                 'grouped in a dispach'),
    }

    def _picking_to_pack_ids(self, cr, uid, picking_ids, context=None):
        move_obj = self.pool['stock.move']
        move_ids = move_obj.search(cr, uid,
                                   [('picking_id', 'in', picking_ids)],
                                   context=context)
        moves = move_obj.read(cr, uid, move_ids, ['tracking_id'],
                              context=context)
        pack_ids = (move['tracking_id'][0] for move in moves)
        return list(set(pack_ids))

    @staticmethod
    def chunks(iterable, size):
        it = iter(iterable)
        while True:
            chunk = tuple(islice(it, size))
            if not chunk:
                return
            yield chunk

    def _group_packs(self, cr, uid, wizard, pack_ids, context=None):
        pack_obj = self.pool['stock.tracking']
        move_obj = self.pool['stock.move']
        dispatch_obj = self.pool['picking.dispatch']

        max_pack = wizard.max_pack

        dispatchs = pack_obj.browse(cr, uid, pack_ids, context=context)

        if max_pack:
            dispatchs = self.chunks(dispatchs, max_pack)
        else:
            dispatchs = [dispatchs]

        for packs in dispatchs:
            dispatch_id = dispatch_obj.create(cr, uid, {}, context=context)
            move_ids = [move.id for pack in packs for move in pack.move_ids]
            move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id},
                           context=context)

    def group(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (tuple, list)):
            assert len(ids) == 1, "expect 1 ID, got %s" % ids
            ids = ids[0]
        model = context.get('active_model')
        assert model in ('stock.picking', 'stock.tracking'), \
            "no supported 'active_model', got %s" % model
        assert context.get('active_ids'), "'active_ids' required"
        pack_ids = context['active_ids']
        if model == 'stock.picking':
            pack_ids = self._picking_to_pack_ids(cr, uid, pack_ids,
                                                 context=context)
        wizard = self.browse(cr, uid, ids, context=context)
        self._group_packs(cr, uid, wizard, pack_ids, context=context)
        return True
