# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import SingleTransactionCase


class BatchGroupTestCase(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        """ Prefer to use SingleTransactionCase because create, confirm
        and assign all pickings + packs creation is quite long.
        """
        SingleTransactionCase.setUpClass()

        cls.wizard_model = cls.env['stock.batch.picking.group']

        product_model = cls.env['product.product']
        cls.p1 = product_model.create({'name': 'Unittest P1'})
        cls.p2 = product_model.create({'name': 'Unittest P2'})
        cls.p3 = product_model.create({'name': 'Unittest P3'})
        cls.p4 = product_model.create({'name': 'Unittest P4'})
        cls.p5 = product_model.create({'name': 'Unittest P5'})
        cls.p6 = product_model.create({'name': 'Unittest P6'})
        cls.p7 = product_model.create({'name': 'Unittest P7'})
        cls.p8 = product_model.create({'name': 'Unittest P8'})
        cls.p9 = product_model.create({'name': 'Unittest P9'})

        cls.stock_loc = cls.env.ref('stock.stock_location_stock')
        cls.customer_loc = cls.env.ref('stock.stock_location_customers')
        cls.all_packs = cls.env['stock.quant.package']

    def setUp(self):
        """ Have to remove pickings from batch, otherwise they can't be put
        in another batch for next tests.
        """
        super(BatchGroupTestCase, self).setUp()
        self.all_packs.mapped('pack_operation_ids').mapped('picking_id').write(
            {'batch_picking_id': False}
        )

    @classmethod
    def create_picking(cls, products):
        picking = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_loc.id,
            'location_dest_id': cls.customer_loc.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': product.id,
                    'product_uom': cls.env.ref('product.product_uom_unit').id,
                    'product_uom_qty': qty,
                    'location_id': cls.stock_loc.id,
                    'location_dest_id': cls.customer_loc.id
                }) for product, qty in products
            ]
        })

        return picking

    @classmethod
    def create_pack_from_picking(cls, picking):
        if picking.state != 'assigned':
            if picking.state != 'confirmed':
                picking.action_confirm()
            picking.force_assign()

        for operation in picking.pack_operation_ids:
            operation.qty_done = operation.product_qty

        picking.put_in_pack()
        return picking.pack_operation_ids.mapped('result_package_id')

    @classmethod
    def create_pack(cls, products):

        picking = cls.create_picking(products)
        package = cls.create_pack_from_picking(picking)

        assert len(package) == 1

        return package

    def _call_wizard(self, options, packs=None):
        wizard = self.wizard_model.create(options)
        if packs is None:
            packs = self.all_packs
        return wizard._group_packs(packs)

    def check_packs(self, batches, packs_list):
        """ Check that packs are correctly dispatch in batches.
        """
        self.assertItemsEqual(
            # In case we got tuple.
            [list(packs) for packs in packs_list],

            [
                sorted(
                    batch.pack_operation_ids.mapped('result_package_id'),
                    key=lambda p: p.id
                )
                for batch in batches
            ]
        )
