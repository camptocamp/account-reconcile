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

from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  ExportMapper)
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            on_record_unlink,
                                            )
from .backend import qoqa
from . import consumer
from .unit.export_synchronizer import QoQaExporter
from .unit.delete_synchronizer import QoQaDeleteSynchronizer
from .unit.backend_adapter import QoQaAdapter


class qoqa_deal_position(orm.Model):
    _inherit = 'qoqa.deal.position'

    _columns = {
        'backend_id': fields.related(
            'deal_id', 'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa'),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }


@on_record_create(model_names='qoqa.deal.position')
@on_record_write(model_names='qoqa.deal.position')
def delay_export(session, model_name, record_id, fields=None):
    # reduce the priority so the deals should be exported before
    consumer.delay_export(session, model_name, record_id,
                          fields=fields, priority=15)

@on_record_unlink(model_names='qoqa.deal.position')
def delay_unlink(session, model_name, record_id):
    consumer.delay_unlink(session, model_name, record_id)


@qoqa
class DealPositionDeleteSynchronizer(QoQaDeleteSynchronizer):
    """ Deal deleter for QoQa """
    _model_name = ['qoqa.deal.position']


@qoqa
class DealPositionExporter(QoQaExporter):
    _model_name = ['qoqa.deal.position']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        binding = self.binding_record
        deal_binder = self.get_binder_for_model('qoqa.deal')
        deal_id = binding.deal_id.id
        deal_qoqa_id = deal_binder.to_backend(deal_id)
        if deal_qoqa_id is None:
            exporter = self.get_connector_unit_for_model(
                    QoQaExporter, 'qoqa.deal')
            exporter.run(deal_id)


@qoqa
class DealPositionAdapter(QoQaAdapter):
    _model_name = 'qoqa.deal.position'
    _endpoint = 'offer'


@qoqa
class DealPositionExportMapper(ExportMapper):
    _model_name = 'qoqa.deal.position'

    direct = [('unit_price', 'unit_price'),
              ('installment_price', 'installment_price'),
              ('regular_price', 'regular_price'),
              ('regular_price_type', 'regular_price_type'),
              ('buy_price', 'buy_price'),
              ('top_price', 'top_price'),
              ('ecotax', 'ecotax'),
              ('date_delivery', 'date_delivery'),
              ('booking_delivery', 'booking_delivery'),
              ('order_url', 'order_url'),
              ('stock_bias', 'stock_bias'),
              ('max_sellable', 'max_sellable'),
              ('lot_size', 'lot_size'),
              ('buyphrase_id', 'buyphrase_id'),
              ('tax_id', 'tax_id'),
              ]
