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
from openerp.osv import orm, fields
from tools.translate import _

class DeliveryCarrierLabelGenerate(orm.TransientModel):

    _inherit = 'delivery.carrier.label.generate'

    _columns = {
        'qty_per_pack': fields.integer(
            'Number of product per pack',
            help='Defines the maximum number of product in a pack. '
                 'We consider each product of the packing has the same size.'),
    }

    def _prepare_packs(self, cr, uid, ids, context=None):
        """ Fill packs with products

        We consider that all product have the same size

        """
        this = self.browse(cr, uid, ids, context=context)[0]

        pickings = [picking
                    for dispatch in this.dispatch_ids
                    for picking in dispatch.related_picking_ids]

        for pick in pickings:
            pick.prepare_packs(max_qty=this.qty_per_pack)


    def action_generate_labels(self, cr, uid, ids, context=None):
        """
        Overide label generation to create packaging first
        """
        this = self.browse(cr, uid, ids, context=context)[0]

        if this.qty_per_pack:
            if not this.dispatch_ids:
                raise orm.except_orm(_('Error'), _('No picking dispatch selected'))

            self._prepare_packs(cr, uid, ids, context=context)

        return super(DeliveryCarrierLabelGenerate, self
                     ).action_generate_labels(cr, uid, ids, context=context)
