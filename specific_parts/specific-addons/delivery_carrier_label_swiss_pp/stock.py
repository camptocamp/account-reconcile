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
from openerp.netsvc import Service


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _generate_swiss_pp_label(self, cr, uid, ids,
                                      tracking_ids=None,
                                      context=None):
        """ Generate labels and write tracking numbers received """
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        company = user.company_id

        assert len(ids) == 1
        report_obj = self.pool.get('ir.actions.report.xml')
        ir_model_data_obj = self.pool.get('ir.model.data')

        __, report_id = ir_model_data_obj.get_object_reference(
            cr, uid, 'delivery', 'shipping_label_swiss_pp_webkit')

        report = report_obj.browse(cr, uid, report_id, context=context)

        data = {'ids': ids}
        report_parser = Service._services['report.%s' % report.report_name]
        pdf_report = report_parser.create_single_pdf(cr, uid, ids,
                                                     data, report,
                                                     context=context)[0]

        return {'name': '%s.pdf' % report.report_name,
                'file': pdf_report,
                'file_type': 'pdf',
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
