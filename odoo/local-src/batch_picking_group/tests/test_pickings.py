# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.exceptions import UserError
from .common import BatchGroupTestCase


class TestGroupPicking(BatchGroupTestCase):

    def setUp(self):
        super(BatchGroupTestCase, self).setUp()

        # For this test we don't use setUpClass because we
        # manipulating pickings states and we want them to be reset.
        self.pick_1 = self.create_picking([
            (self.p1, 10),
            (self.p2, 10),
        ])

        self.pick_2 = self.create_picking([
            (self.p1, 10),
            (self.p2, 10),
        ])

    def test_no_packs(self):
        wizard = self.wizard_model.with_context(
            active_model='stock.picking',
            active_ids=[self.pick_1.id, self.pick_2.id]
        ).create({})

        with self.assertRaises(UserError):
            wizard.group()

    def test_picking_no_pack_operation(self):
        self.create_pack_from_picking(self.pick_1)

        wizard = self.wizard_model.with_context(
            active_model='stock.picking',
            active_ids=[self.pick_1.id, self.pick_2.id]
        ).create({})

        result = wizard.group()
        # pick_1 has been put in a batch
        self.assertTrue(self.pick_1.batch_picking_id)

        # Result open a warning wizard
        self.assertEqual('stock.batch.group.warnings', result['res_model'])
        self.assertEqual('new', result['target'])
        self.assertEqual({
            'warning_picking_ids': [self.pick_2.id],
            'batch_domain': "[('id', 'in', %s)]"
                            % [self.pick_1.batch_picking_id.id],
        }, result['context'])

    def test_good_packs(self):
        self.create_pack_from_picking(self.pick_1)
        self.create_pack_from_picking(self.pick_2)

        wizard = self.wizard_model.with_context(
            active_model='stock.picking',
            active_ids=[self.pick_1.id, self.pick_2.id]
        ).create({})

        result = wizard.group()
        batch_id = self.pick_1.batch_picking_id
        self.assertTrue(batch_id)
        self.assertEqual(batch_id, self.pick_2.batch_picking_id)

        # Result open stock.batch.picking tree view
        self.assertEqual('stock.batch.picking', result['res_model'])
        self.assertEqual(
            "[('id', 'in', %s)]" % [self.pick_1.batch_picking_id.id],
            result['domain']
        )

    def test_picking_wrong_state(self):
        self.create_pack_from_picking(self.pick_1)
        self.create_pack_from_picking(self.pick_2)

        self.pick_2.action_cancel()

        wizard = self.wizard_model.with_context(
            active_model='stock.picking',
            active_ids=[self.pick_1.id, self.pick_2.id]
        ).create({})

        wizard.group()

        # pick_1 has been put in a batch
        self.assertTrue(self.pick_1.batch_picking_id)

        # Pick2 has been ignored
        self.assertFalse(self.pick_2.batch_picking_id)

    def test_call_group_with_packs(self):
        pack1 = self.create_pack_from_picking(self.pick_1)
        pack2 = self.create_pack_from_picking(self.pick_2)

        wizard = self.wizard_model.with_context(
            active_model='stock.quant.package',
            active_ids=[pack1.id, pack2.id]
        ).create({})

        result = wizard.group()

        batch_id = self.pick_1.batch_picking_id
        self.assertTrue(batch_id)
        self.assertEqual(batch_id, self.pick_2.batch_picking_id)

        # Result open stock.batch.picking tree view
        self.assertEqual('stock.batch.picking', result['res_model'])
        self.assertEqual(
            "[('id', 'in', %s)]" % [self.pick_1.batch_picking_id.id],
            result['domain']
        )

    def test_picking_not_in_pack(self):
        self.create_pack_from_picking(self.pick_1)

        # pack2 is available but not in a package
        self.pick_2.action_confirm()
        self.pick_2.force_assign()

        wizard = self.wizard_model.with_context(
            active_model='stock.picking',
            active_ids=[self.pick_1.id, self.pick_2.id]
        ).create({})

        with self.assertRaises(UserError):
            wizard.group()

    def test_warning_wizard(self):

        self.pick_1.name = 'TEST/PICK1'
        self.pick_2.name = 'TEST/PICK2'

        warning_wizard = self.env['stock.batch.group.warnings'].with_context(
            warning_picking_ids=[self.pick_1.id, self.pick_2.id],
            batch_domain='fake_domain',
        ).create({})

        self.assertEqual(
            "<p>"
            "The following pickings were ignored because they contain "
            "zero or more than one package:"
            "</p>"
            "<ul><li>TEST/PICK1</li><li>TEST/PICK2</li></ul>",
            warning_wizard.message
        )

        result = warning_wizard.action_ok()
        self.assertEqual('stock.batch.picking', result['res_model'])
        self.assertEqual('fake_domain', result['domain'])
