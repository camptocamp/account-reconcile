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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class picking_split_packs(orm.TransientModel):

    _name = 'picking.split.packs'

    _columns = {
        'qty_per_pack': fields.integer(
            'Number of product per pack',
            required=True,
            help='Defines the maximum number of product in a pack. '
                 'We consider each product of the packing has the same size.'),
    }

    _defaults = {
        'qty_per_pack': 1,
    }

    _sql_constraints = [
        ('qty_per_pack_number', 'CHECK (qty_per_pack > 0)',
         'The number of products per pack must be above 0.'),
    ]

    def _split_packs(self, cr, uid, wizard, picking_ids, context=None):
        """ Fill packs with products

        We consider that all product have the same size

        """
        picking_obj = self.pool['stock.picking']
        picking_obj.prepare_packs(cr, uid, picking_ids,
                                  max_qty=wizard.qty_per_pack,
                                  context=context)
        pickings = picking_obj.browse(cr, uid, picking_ids, context=context)
        pack_ids = list(set(move.tracking_id.id for picking in pickings
                            for move in picking.move_lines
                            if move.tracking_id))
        return pack_ids

    def split_packs(self, cr, uid, ids, context=None):
        if isinstance(ids, (tuple, list)):
            assert len(ids) == 1, "expect 1 ID, got %s" % ids
            ids = ids[0]
        assert context.get('active_ids'), "'active_ids' required"
        picking_ids = context['active_ids']

        wizard = self.browse(cr, uid, ids, context=context)
        pack_ids = self._split_packs(cr, uid, wizard,
                                     picking_ids, context=context)

        return {
            'domain': "[('id', 'in', %s)]" % pack_ids,
            'name': _('Generated Packs'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.tracking',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
