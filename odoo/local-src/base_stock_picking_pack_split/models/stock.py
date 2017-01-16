# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import _, api, exceptions, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def _split_into_quantity(self, quantity):
        """ Split an operation into two

        The quantity express the quantity to leave in the current operation.

        """
        self.ensure_one()
        package_model = self.env['stock.quant.package']
        if quantity > self.product_qty:
            raise exceptions.UserError(
                _('Total quantity after split exceeds the '
                  'quantity to split for this product: '
                  '"%s" (id: %d).') % (self.product_id.name,
                                       self.product_id.id))
        quantity_rest = self.product_qty - quantity
        if quantity > 0:
            assert self.result_package_id
            self.write({'product_qty': quantity,
                        'qty_done': quantity,
                        })

        if quantity_rest > 0:
            pack = package_model.create({})
            if quantity == 0.0:
                self.result_package_id = pack
            else:
                default_val = {
                    'product_qty': quantity_rest,
                    'result_package_id': pack.id,
                    'qty_done': quantity_rest,
                }
                current_op = self.copy(default_val)
                return current_op
        return self


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def prepare_packs(self, max_qty=1):
        """ Fill packs with products

        We consider that all product of the picking have the same size.

        A pack will be filled by a type of product, if some space is left
        then we try to fill it with the products of the next picking line
        and so on...

        """
        package_model = self.env['stock.quant.package']
        for pick in self:
            if pick.state in ('cancel', 'done'):
                continue

            # we have to set destination packages on operations
            op_to_split = [op for op in pick.pack_operation_product_ids
                           if not op.result_package_id]

            last_pack = package_model.browse()
            while op_to_split:
                op = op_to_split.pop()
                # Set a result_package_id on the operation, the value is the
                # last one of another operation of the same picking, or a new
                # one if the last operation hadn't a package
                if not op.result_package_id:
                    if not last_pack:
                        last_pack = package_model.create({})
                    op.result_package_id = last_pack

                # ORM is too slow here
                self.env.cr.execute(
                    "SELECT SUM(product_qty) "
                    "FROM stock_pack_operation "
                    "WHERE picking_id = %s "
                    "AND result_package_id = %s "
                    "AND product_id IS NOT NULL",
                    (pick.id, op.result_package_id.id)
                )
                pack_qty = self.env.cr.fetchone()[0]
                if pack_qty == max_qty:
                    op.qty_done = op.product_qty
                    continue

                if pack_qty > max_qty:
                    qty_to_pack = op.product_qty - (pack_qty - max_qty)
                    last_op = op._split_into_quantity(qty_to_pack)
                    last_pack = last_op.result_package_id
                    op_to_split.append(last_op)

            return True
