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
        'pack_limit': fields.integer(
            'Limit of packs',
            help='The number of packs per dispatch will be limited to this '
                 'quantity. Leave 0 to set no limit.'),
        'pack_limit_apply_threshold': fields.integer(
            'No limit below',
            help='The limit is not applied when the packs contains '
                 'this number or less of products. Does only apply to '
                 'the dispatchs grouped with similar content.\n'
                 'Set to 0 to always apply the limit.'),
        'only_product_ids': fields.many2many(
            'product.product',
            string='Filter on products',
            help='Dispatchs will be created only if the content of the '
                 'pack contains exactly the same products than selected '
                 '(without consideration for the quantity).\n'
                 'No filter is applied when no product is selected.'),
        'group_by_content': fields.boolean(
            'Group By Content',
            help='Packs with similar content will be grouped in '
                 'the same dispatch'),
        'group_leftovers': fields.boolean(
            'Group Leftovers',
            help='Leftovers are dispatchs generated and containing a '
                 'number of packs below a threshold. This option will '
                 'group them all in a final dispatch'),
        'group_leftovers_threshold': fields.integer(
            'Threshold',
            help='Generated dispatchs are considered as leftovers when '
                 'they have a less or equal number of packs than the '
                 'threshold.\n'
                 'With the default value of 1, the dispatchs with 1 pack '
                 'will be grouped in a final dispatch.')
    }

    _defaults = {
        'pack_limit_apply_threshold': 1,
        'group_by_content': True,
        'group_leftovers': True,
        'group_leftovers_threshold': 1,
    }

    def _picking_to_pack_ids(self, cr, uid, picking_ids, context=None):
        """ Get the pack ids from picking ids """
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
        """ Chunk iterable to n parts of size `size` """
        it = iter(iterable)
        while True:
            chunk = tuple(islice(it, size))
            if not chunk:
                return
            yield chunk

    def _filter_packs(self, cr, uid, wizard, packs, context=None):
        """ Filter the packs. Their content should equal to the filter """
        if not wizard.only_product_ids:
            return packs
        filter_product_ids = set(pr.id for pr in wizard.only_product_ids)
        keep = []
        for pack in packs:
            product_ids = set(move.product_id.id for move in pack.move_ids)
            if product_ids != filter_product_ids:
                continue
            keep.append(pack)
        return keep

    @staticmethod
    def _pack_sort_key(pack):
        """ Sort key used for the grouping of the packs """
        # sort the moves so they are compared equally,
        # e.g. avoid to compare [(1, 10), (2, 20)] vs [(2, 20), (1, 10)]
        sorted_moves = sorted(pack.move_ids,
                              key=lambda m: (m.product_id.id,
                                             m.product_qty,
                                             m.product_uom.id))
        return [(move.product_id.id, move.product_qty, move.product_uom.id) for
                move in sorted_moves]

    def _group_by_content(self, cr, uid, wizard, packs, context=None):
        """ Group the packs by the equality of their content """
        if wizard.group_by_content:
            packs = sorted(packs, key=self._pack_sort_key)
            for _content, gpacks in groupby(packs, self._pack_sort_key):
                yield list(gpacks)
        else:
            # one dispatch with all the packs
            yield packs

    def _split_dispatchs_to_limit(self, cr, uid, wizard, dispatchs,
                                  allow_threshold=False, context=None):
        """ Split the dispatchs having a count of packs above the limit

        Threshold should not be applied when a dispatch has packs
        of disparate content.  The content is the same when the option
        group_by_content is used and the dispatch is not a leftover

        """
        pack_limit = wizard.pack_limit
        threshold = wizard.pack_limit_apply_threshold
        for packs in dispatchs:
            # only make sense for groups when all the packs have the
            # same content
            if allow_threshold and threshold:
                first_pack = packs[0]
                # ignore the limit when below the threshold
                if len(first_pack.move_ids) <= threshold:
                    yield packs
                    continue
            if pack_limit:
                for chunk in self.chunks(packs, pack_limit):
                    yield chunk
            else:
                yield packs

    def _dispatch_leftovers(self, cr, uid, wizard, dispatchs, context=None):
        """ Find the leftovers dispatchs and group them in a final dispatch.

        Leftovers are dispatchs containing less packs than a defined
        threshold (1 by default).  The leftovers may be grouped in one
        (or several when using a limit of packs per dispatch) dispatch
        to avoid having one dispatch for each unique pack.

        """
        group_leftovers = wizard.group_leftovers
        threshold = wizard.group_leftovers_threshold
        leftovers = []
        for packs in dispatchs:
            if group_leftovers:
                if len(packs) <= threshold:
                    leftovers += packs
                else:
                    yield packs
            else:
                yield packs

        if leftovers:
            # we should re-apply the limit on the leftovers
            leftovers = self._split_dispatchs_to_limit(cr, uid, wizard,
                                                       [leftovers],
                                                       # applied only on
                                                       # groups of
                                                       # similar content
                                                       allow_threshold=False,
                                                       context=context)
            for leftover in leftovers:
                yield leftover

    def _create_dispatch(self, cr, uid, vals, packs, context=None):
        """ Create a dispatch for packs """
        move_obj = self.pool['stock.move']
        dispatch_obj = self.pool['picking.dispatch']
        dispatch_id = dispatch_obj.create(cr, uid, vals, context=context)
        move_ids = [move.id for pack in packs for move in pack.move_ids]
        move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id},
                       context=context)
        return dispatch_id

    def _read_packs(self, cr, uid, wizard, pack_ids, context=None):
        pack_obj = self.pool['stock.tracking']
        return pack_obj.browse(cr, uid, pack_ids, context=context)

    def _group_packs(self, cr, uid, wizard, pack_ids, context=None):
        """ Split a set of packs in many dispatches according to rules """
        packs = self._read_packs(cr, uid, wizard, pack_ids, context=context)
        packs = self._filter_packs(cr, uid, wizard, packs, context=context)
        dispatchs = self._group_by_content(cr, uid, wizard, packs,
                                           context=context)
        dispatchs = self._split_dispatchs_to_limit(
            cr, uid, wizard,
            # no threshold allowed when the content of the packs may be
            # different
            dispatchs, allow_threshold=wizard.group_by_content,
            context=context)
        # done after the split because the split can create new
        # leftovers by leaving a pack alone in a picking dispatch
        dispatchs = self._dispatch_leftovers(cr, uid, wizard, dispatchs,
                                             context=context)

        created_ids = []
        for packs in dispatchs:
            dispatch_id = self._create_dispatch(cr, uid, {}, packs,
                                                context=context)
            created_ids.append(dispatch_id)
        return created_ids

    def group(self, cr, uid, ids, context=None):
        """ Public method to use the wizard.

        Can be used from Delivery Orders or Packs.
        When used with Delivery Orders, it consumes all the packs
        of the selected delivery orders.

        """
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
