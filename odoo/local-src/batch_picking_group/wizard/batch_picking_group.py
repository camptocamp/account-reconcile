# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from itertools import islice, groupby
from collections import namedtuple, defaultdict
from openerp import _, api, fields, models
from openerp.exceptions import UserError

# packs: list of packs
# group: boolean, True means that all the packs are identical
# leftover: means it is the result of grouping all the leftovers
# leftover_size: quantity of products in the packs of the leftover
# batch (leftovers are grouped by quantity of products

PreparedBatch = namedtuple('PreparedBatch',
                           'packs group leftover leftover_size')


class BatchPickingGroup(models.TransientModel):
    _name = 'stock.batch.picking.group'
    _description = 'Batch Picking Grouping'

    pack_limit = fields.Integer(
        'Number of packs',
        help='The number of packs per batch will be limited to this '
             'quantity. Leave 0 to set no limit.'
    )
    pack_limit_apply_threshold = fields.Boolean(
        'No limit for 1 unit',
        default=True,
        help='The limit is not applied when the packs contains '
             'only 1 unit. Does only apply to '
             'the batches grouped with similar content.'
    )
    only_product_ids = fields.Many2many(
        'product.product',
        string='Filter on products',
        help='Batches will be created only if the content of the '
             'pack contains exactly the same products than selected '
             '(without consideration for the quantity).\n'
             'No filter is applied when no product is selected.'
    )
    group_by_content = fields.Boolean(
        'Group By Content',
        default=True,
        help='Packs with similar content will be grouped in '
             'the same batch'
    )
    group_leftovers = fields.Boolean(
        'Group Leftovers',
        default=True,
        help='Leftovers are batches generated and containing a '
             'number of packs below a threshold. This option will '
             'group them all in a final batch'
    )
    group_leftovers_threshold = fields.Integer(
        'Threshold',
        default=1,
        help='Generated batches are considered as leftovers when '
             'they have a less or equal number of packs than the '
             'threshold.\n'
             'With the default value of 1, the batches with 1 pack '
             'will be grouped in a final batch.'
    )
    suffix = fields.Char('Suffix')

    _sql_constraints = [
        ('pack_limit_number', 'CHECK (pack_limit >= 0)',
         'The pack limit must be equal or above 0.'),
        ('group_leftovers_threshold_number',
         'CHECK (group_leftovers_threshold >= 1)',
         'The Leftovers threshold must be above 0.'),
    ]

    def _picking_to_packs(self, picking_ids):
        """ Get the pack ids from picking ids
        """
        operations = self.env['stock.pack.operation'].search([
            ('picking_id', 'in', picking_ids),
        ])

        operations, warnings = self._check_pickings_packs(
            picking_ids, operations
        )

        return operations.mapped('result_package_id'), warnings

    @staticmethod
    def _check_pickings_packs(picking_ids, operations):
        pickings_packs = defaultdict(set)
        for op in operations:
            if not op.result_package_id:
                raise UserError(_(
                    "Some selected pickings contain products "
                    "that are not in packages"
                ))
            pickings_packs[op.picking_id.id].add(op.result_package_id)

        warnings = []
        for pick_id in picking_ids:
            package_ids = pickings_packs[pick_id]
            if len(package_ids) != 1:
                warnings.append(pick_id)

        operations = operations.filtered(
            lambda o: o.picking_id.id not in warnings
        )
        return operations, warnings

    @staticmethod
    def chunks(iterable, size):
        """ Chunk iterable to n parts of size `size`
        """
        it = iter(iterable)
        while True:
            chunk = tuple(islice(it, size))
            if not chunk:
                return
            yield chunk

    def _filter_pack(self, pack):
        """ Return True if pack content match wizard filters

        :type pack: stock_package
        :rtype: bool
        """
        for operation in pack.pack_operation_ids:
            # Exclude packs that are in canceled or done pickings.
            if operation.picking_id.state in ('cancel', 'done'):
                return False

            # Exclude pack if some picking already in batch
            if operation.picking_id.batch_picking_id:
                return False

        if self.only_product_ids:
            return self.only_product_ids == pack.mapped(
                'pack_operation_ids.product_id'
            )

        return True

    @staticmethod
    def _pack_group_key(pack):
        """ Sort key used for the grouping of the packs """
        # sort the operations so they are compared equally,
        # e.g. avoid to compare [(1, 10), (2, 20)] vs [(2, 20), (1, 10)]

        return sorted(
            [(op.product_id.id, op.product_qty, op.product_uom_id.id)
             for op in pack.pack_operation_ids]
        )

    @classmethod
    def _pack_sort_key(cls, pack):
        """ Just add pack id to group_key for keeping same order for testing.
        """
        return cls._pack_group_key(pack), pack.id

    def _group_by_content(self, packs):
        """ Group the packs by the equality of their content
        """
        if self.group_by_content:
            packs = packs.sorted(key=self._pack_sort_key)
            for _content, gpacks in groupby(packs, self._pack_group_key):
                yield PreparedBatch(list(gpacks), group=True,
                                    leftover=False, leftover_size=None)
        else:
            # One batch with all the packs.
            yield PreparedBatch(packs, group=False,
                                leftover=False, leftover_size=None)

    def _split_batches_to_limit(self, batches):
        """ Split the batches having a count of packs above the limit

        Threshold should not be applied when a batch has packs
        of disparate content.  The content is the same when the option
        group_by_content is used and the batch is not a leftover
        """
        for packs, group, leftover, leftover_size in batches:
            # only make sense for groups when all the packs have the
            # same content
            if group and self.pack_limit_apply_threshold:
                first_pack = packs[0]
                # ignore the limit when below the threshold
                if (len(first_pack.pack_operation_ids) == 1 and
                        first_pack.pack_operation_ids[0].product_qty == 1):
                    yield PreparedBatch(packs, group=group,
                                        leftover=leftover,
                                        leftover_size=leftover_size)
                    continue
            if self.pack_limit:
                for chunk in self.chunks(packs, self.pack_limit):
                    yield PreparedBatch(chunk, group=group,
                                        leftover=leftover,
                                        leftover_size=leftover_size)
            else:
                yield PreparedBatch(packs, group=group,
                                    leftover=leftover,
                                    leftover_size=leftover_size)

    def _dispatch_leftovers(self, batches):
        """ Find the leftovers batches and group them in a final batch.

        Leftovers are batches containing less packs than a defined
        threshold (1 by default).  The leftovers may be grouped in one
        (or several when using a limit of packs per batch) batch
        to avoid having one batch for each unique pack.
        """
        leftovers_packs = []
        leftovers_threshold = self.group_leftovers_threshold
        for packs, group, leftover, leftover_size in batches:
            if self.group_leftovers and len(packs) <= leftovers_threshold:
                leftovers_packs += packs

            else:
                yield PreparedBatch(
                    packs, group=group,
                    leftover=leftover, leftover_size=leftover_size
                )

        if leftovers_packs:
            yield PreparedBatch(leftovers_packs, group=False,
                                leftover=True, leftover_size=None)

    @staticmethod
    def _leftovers_group_key(pack):
        """ Used to split leftover batches according to the quantity
        of products.
        """
        return sum(op.product_qty for op in pack.pack_operation_ids),

    @classmethod
    def _leftovers_sort_key(cls, pack):
        """ Just add pack id to group_key for keeping same order for testing.
        """
        return cls._leftovers_group_key(pack), pack.id

    def _group_leftovers(self, batches):
        """ Group leftovers by number of products.

        The leftovers are packs of mixed content and it would help if
        packs are grouped by total quantity of product in leftovers so
        batches have all the same quantity of products.
        """
        leftovers = []
        for prepared_batch in batches:
            if not prepared_batch.leftover:
                yield prepared_batch
                continue

            packs = sorted(prepared_batch.packs, key=self._leftovers_sort_key)

            for qty, gpacks in groupby(packs, self._leftovers_group_key):
                batch = PreparedBatch(
                    list(gpacks), group=prepared_batch.group,
                    leftover=prepared_batch.leftover,
                    leftover_size=qty
                )

                # we must re-apply the limit on the leftovers
                split = self._split_batches_to_limit([batch])
                for prepared in split:
                    leftovers.append(prepared)

        if leftovers:
            # one more time, but only on the leftovers, so if batches
            # have been generated below the threshold, we group them
            # again in a "leftover of leftovers".
            leftovers = self._dispatch_leftovers(leftovers)
            leftovers = self._split_batches_to_limit(leftovers)
            for prepared_batch in leftovers:
                yield prepared_batch

    def _create_batch(self, name, packs):
        """ Create a batch for packs.
        """
        batch = self.env['stock.batch.picking'].create({
            'name': name,
        })
        pickings = self.env['stock.picking']
        for pack in packs:
            pickings |= pack.pack_operation_ids.mapped('picking_id')\

        pickings.write({
            'batch_picking_id': batch.id
        })
        return batch

    def _get_batches_name(self, prepared_batch):
        name = self.env['ir.sequence'].next_by_code('stock.batch.picking')
        nb_packs = len(prepared_batch.packs)

        descr = None
        if not (prepared_batch.group or prepared_batch.leftover):
            descr = _('%d packs of mixed content') % nb_packs

        # a grouped leftover should not happen
        elif prepared_batch.leftover:
            size = prepared_batch.leftover_size
            if size is None:
                descr = (_('%d packs of leftovers with various units')
                         % nb_packs)
            else:
                descr = (_('%d packs of leftovers with %s units')
                         % (nb_packs, size))

        elif prepared_batch.group:
            prods = [
                _("%sx[%s]") % (op.product_qty, op.product_id.default_code)
                for op in prepared_batch.packs[0].pack_operation_ids
                ]
            descr = _('%d packs grouped by: %s') % (
                nb_packs, ' + '.join(prods)
            )

        name = ' - '.join([part for part in (name, self.suffix, descr)
                           if part])
        return name

    def _group_packs(self, packs):
        """ Split a set of packs in many batches according to rules
        """
        packs = packs.filtered(self._filter_pack)
        if not packs:
            raise UserError(_('No available packages to group.'))

        prepared_batches = self._group_by_content(packs)
        prepared_batches = self._split_batches_to_limit(prepared_batches)
        # done after the split because the split can create new
        # leftovers by leaving a pack alone in a batch picking.
        prepared_batches = self._dispatch_leftovers(prepared_batches)
        prepared_batches = self._group_leftovers(prepared_batches)

        batches = self.env['stock.batch.picking']
        for prepared_batch in prepared_batches:
            name = self._get_batches_name(prepared_batch)
            batches |= self._create_batch(name, prepared_batch.packs)

        return batches

    @api.multi
    def group(self):
        """ Public method to use the wizard.

        Can be used from Delivery Orders or Packs.
        When used with Delivery Orders, it consumes all the packs
        of the selected delivery orders.
        """
        self.ensure_one()

        source_model = self.env.context.get('active_model')
        assert source_model in ('stock.picking', 'stock.quant.package'), \
            "unexpected 'active_model', got %s" % source_model

        assert self.env.context.get('active_ids'), "'active_ids' required"
        active_ids = self.env.context['active_ids']

        if source_model == 'stock.picking':
            packs, warnings = self._picking_to_packs(active_ids)
        else:
            warnings = []
            packs = self.env['stock.quant.package'].browse(active_ids)

        batches = self._group_packs(packs)
        batch_domain = "[('id', 'in', %s)]" % batches.ids

        if warnings:
            return {
                'name': _('Generated Batches Warning'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.batch.group.warnings',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'warning_picking_ids': warnings,
                    'batch_domain': batch_domain
                }
            }
        else:
            return {
                'domain': batch_domain,
                'name': _('Generated Batches'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.batch.picking',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
