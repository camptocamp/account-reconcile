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

from itertools import islice, groupby
from openerp.osv import orm, fields


class picking_dispatch_grouper(orm.TransientModel):
    _name = 'picking.dispatch.grouper'
    _description = 'Picking Dispatch Grouper'

    _columns = {
        'max_pack': fields.integer(
            'Limit of packs',
            help='The number of packs per dispatch will be limited to this '
                 'quantity. Leave 0 to set no limit.'),
        'only_product_ids': fields.many2many(
            'product.product',
            string='Filter on products',
            help='Dispatchs will be created only if the content of the '
                 'pack contains exactly the same content '
                 '(without consideration for the quantity).\n'
                 'No filter is applied when no product is selected.'),
        'group_by_content': fields.boolean(
            'Group By Content',
            help='Packs with similar content will be grouped in '
                 'the same dispatch'),
        'group_leftovers': fields.boolean(
            'Put the leftovers in the same dispatch',
            help='When packs do not fall in a group, they will all be '
                 'grouped in a dispatch'),
        'group_leftovers_limit': fields.integer(
            'Size of leftovers',
            help='A group of packs with the same content is considered '
                 'as a leftover below this number. With the default '
                 'value of 1, only the packs with a unique content '
                 'will be grouped in the leftovers dispatch.')
    }

    _defaults = {
        'group_by_content': True,
        'group_leftovers': True,
        'group_leftovers_limit': 1,
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

    @staticmethod
    def _pack_sort_key(pack):
        sorted_moves = sorted(pack.move_ids,
                              key=lambda m: (m.product_id.id,
                                             m.product_qty,
                                             m.product_uom.id))
        return [(move.product_id.id, move.product_qty, move.product_uom.id) for
                move in sorted_moves]

    def _filter_packs(self, cr, uid, wizard, packs, context=None):
        filter_product_ids = set(pr.id for pr in wizard.only_product_ids)
        for pack in packs:
            product_ids = set(move.product_id.id for move in pack.move_ids)
            if product_ids != filter_product_ids:
                continue
            yield pack

    def _group_packs(self, cr, uid, wizard, pack_ids, context=None):
        pack_obj = self.pool['stock.tracking']
        move_obj = self.pool['stock.move']
        dispatch_obj = self.pool['picking.dispatch']

        max_pack = wizard.max_pack
        group_by_content = wizard.group_by_content
        group_leftovers = wizard.group_leftovers
        group_leftovers_limit = wizard.group_leftovers_limit

        packs = pack_obj.browse(cr, uid, pack_ids, context=context)

        if wizard.only_product_ids:
            packs = self._filter_packs(cr, uid, wizard, packs, context=context)

        if group_by_content:
            packs = sorted(packs, key=self._pack_sort_key)
            dispatchs = (list(gpacks) for _content, gpacks in
                         groupby(packs, self._pack_sort_key))

        else:
            # one dispatch with all the packs
            dispatchs = [packs]

        if max_pack:
            dispatchs = (chunk for dispatch in dispatchs
                         for chunk in self.chunks(dispatch, max_pack))

        # done after the split because the split can create new
        # leftovers by leaving a pack alone in a picking dispatch
        if group_leftovers:
            leftovers = []
            group_dispatchs = []
            for packs in dispatchs:
                if len(packs) <= group_leftovers_limit:
                    leftovers += packs
                else:
                    group_dispatchs.append(packs)
            if leftovers:
                # we should re-apply the limit on the leftovers
                if max_pack:
                    group_dispatchs += self.chunks(leftovers, max_pack)
                else:
                    group_dispatchs.append(leftovers)
            dispatchs = group_dispatchs

        created_ids = []
        for packs in dispatchs:
            dispatch_id = dispatch_obj.create(cr, uid, {}, context=context)
            move_ids = [move.id for pack in packs for move in pack.move_ids]
            move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id},
                           context=context)
            created_ids.append(dispatch_id)
        return created_ids

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
