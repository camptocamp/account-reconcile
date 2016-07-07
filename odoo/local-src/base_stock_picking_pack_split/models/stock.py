# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import _, api, exceptions, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def _split_into_quantity(self, quantity):
        """ Optimized version of the wizard stock.split.into

        Contrary to the wizard, it returns the the new operation.
        Also, it does not call op.setlast_package() if it is not
        necessary.
        """
        self.ensure_one()
        Package = self.env['stock.quant.package']
        if quantity > self.product_qty:
            raise exceptions.UserError(
                _('Total quantity after split exceeds the '
                  'quantity to split for this product: '
                  '"%s" (id: %d).') % (self.product_id.name,
                                       self.product_id.id))
        quantity_rest = self.product_qty - quantity
        if quantity > 0:
            if not self.result_package_id:
                self.setlast_package()
            self.write({'product_qty': quantity,
                        'qty_done': quantity,
                        })

        if quantity_rest > 0:
            pack = Package.create({})
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

    @api.multi
    def setlast_package(self):
        """ Optimized version of setlast_package

        Can be removed once a PR is merged:
            https://github.com/odoo/odoo/pull/2448
            https://github.com/OCA/OCB/pull/49

        """
        self.ensure_one()
        Package = self.env['stock.quant.package']
        if self.picking_id:
            ops = self.search([('picking_id', '=', self.picking_id.id),
                              ('result_package_id', '!=', False)])
            # somehow order attribute for search doesn't work

            if ops:
                packs = ops.mapped('result_package_id')
                pack = packs.sorted(lambda rec: rec.id)[-1]
            else:
                pack = Package.create({})
            self.result_package_id = pack
        return True


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
        for pick in self:
            if pick.state in ('cancel', 'done'):
                continue

            # copy this list of op
            op_to_split = [op for op in pick.pack_operation_product_ids
                           if not op.result_package_id]

            while op_to_split:
                op = op_to_split.pop()
                # Set a result_package_id on the operation, the value is the
                # last one of another operation of the same picking, or a new
                # one if the last picking hadn't a package
                if not op.result_package_id:
                    op.setlast_package()
                # ensure written change is readable
                op.refresh()

                pack_qty = sum(p.product_qty for p
                               in pick.pack_operation_product_ids
                               if p.result_package_id == op.result_package_id)
                if pack_qty == max_qty:
                    op.qty_done = op.product_qty
                    continue

                if pack_qty > max_qty:
                    qty_to_pack = op.product_qty - (pack_qty - max_qty)
                    new_op = op._split_into_quantity(qty_to_pack)

                    if new_op:
                        op_to_split.append(new_op)
                    else:
                        # If qty to split == op qty (qty_to_pack == 0),
                        # the move was simply given a new result_package_id.
                        # We add it to check it again.
                        op_to_split.append(op)
        return True
