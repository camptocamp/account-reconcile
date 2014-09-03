# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
from openerp.osv import orm
from openerp.netsvc import LocalService


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _generate_swiss_pp_label(self, cr, uid, ids, tracking_ids=None,
                                 context=None):
        """ Generate labels and write tracking numbers received """
        assert len(ids) == 1
        report_name = 'delivery.shipping.label.swiss.pp.webkit'
        service = LocalService('report.%s' % report_name)
        result, __ = service.create(cr, uid, ids, {}, context=context)

        return {'name': '%s.pdf' % report_name,
                'file': result,
                'file_type': 'pdf',
                'tracking_id': tracking_ids and tracking_ids[0],
                }

    def generate_shipping_labels(self, cr, uid, ids, tracking_ids=None,
                                 context=None):
        """ Add label generation for Swiss Post PP Franking"""
        if isinstance(ids, (long, int)):
            ids = [ids]
        assert len(ids) == 1
        picking = self.browse(cr, uid, ids[0], context=context)
        if picking.carrier_id.type == 'swiss_apost':
            return [self._generate_swiss_pp_label(
                cr, uid, ids,
                tracking_ids=tracking_ids,
                context=context)]
        return super(stock_picking, self).\
            generate_shipping_labels(cr, uid, ids, tracking_ids=tracking_ids,
                                     context=context)
