# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

import json
from openerp.osv import orm, fields
from openerp.addons.connector_ecommerce.event import on_picking_out_done
from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_stock_picking(orm.Model):
    _name = 'qoqa.stock.picking'
    _inherit = 'qoqa.binding'
    _inherits = {'stock.picking': 'openerp_id'}
    _description = 'QoQa Delivery Order'

    _columns = {
        'openerp_id': fields.many2one('stock.picking.out',
                                      string='Delivery Order',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
        'qoqa_sale_binding_id': fields.many2one(
            'qoqa.sale.order',
            string='QoQa Sale Order',
            ondelete='set null'),
        'exported': fields.boolean('Exported'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A delivery order with the same ID on QoQa already exists"),
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A delivery order can be exported only once on the same backend"),
    ]


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.stock.picking',
            'openerp_id',
            string='QBindings for Delivery Orders'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(stock_picking, self).copy_data(cr, uid, id,
                                                    default=default,
                                                    context=context)


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.stock.picking',
            'openerp_id',
            string='QBindings for Delivery Orders'),
    }


@on_picking_out_done
def picking_done_create_binding(session, model_name, record_id,
                                picking_method):
    """ Create a binding for the picking so it will be exported. """
    picking = session.browse(model_name, record_id)
    sale = picking.sale_id
    if not sale:
        return
    if not sale.qoqa_bind_ids:
        return  # does not comes from QoQa

    # if no tracking ref on picking and no pack where defined,
    # we don't want to export trackings
    if (not picking.carrier_tracking_ref
            and not any(line.tracking_id for line in picking.move_lines)):
        return

    for sale_binding in sale.qoqa_bind_ids:
        session.create('qoqa.stock.picking',
                       {'backend_id': sale_binding.backend_id.id,
                        'openerp_id': picking.id,
                        'qoqa_sale_binding_id': sale_binding.id,
                        'picking_method': picking_method})


@qoqa
class QoQaPickingLabelAdapter(QoQaAdapter):
    _model_name = 'qoqa.picking.label'
    _endpoint = 'label'

    def add_trackings(self, vals):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.post(url + 'generate_shippments',
                                    data=json.dumps(vals),
                                    headers=headers)
        self._handle_response(response)
