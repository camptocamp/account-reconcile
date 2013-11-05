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

from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  ExportMapper)
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            on_record_unlink,
                                            )
from ..backend import qoqa
from .. import consumer
from ..unit.export_synchronizer import QoQaExporter
from ..unit.delete_synchronizer import QoQaDeleteSynchronizer
from ..unit.mapper import m2o_to_backend


@on_record_create(model_names='qoqa.offer.position')
@on_record_write(model_names='qoqa.offer.position')
def delay_export(session, model_name, record_id, fields=None):
    # reduce the priority so the offers should be exported before
    consumer.delay_export(session, model_name, record_id,
                          fields=fields, priority=15)


@on_record_unlink(model_names='qoqa.offer.position')
def delay_unlink(session, model_name, record_id):
    consumer.delay_unlink(session, model_name, record_id)


@qoqa
class OfferPositionDeleteSynchronizer(QoQaDeleteSynchronizer):
    """ Offer deleter for QoQa """
    _model_name = ['qoqa.offer.position']


@qoqa
class OfferPositionExporter(QoQaExporter):
    _model_name = ['qoqa.offer.position']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        binding = self.binding_record
        self._export_dependency(binding.offer_id, 'qoqa.offer')
        self._export_dependency(binding.product_tmpl_id,
                                'qoqa.product.template')

@qoqa
class OfferPositionExportMapper(ExportMapper):
    _model_name = 'qoqa.offer.position'

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
              (m2o_to_backend('tax_id'), 'tax_id'),
              (m2o_to_backend('offer_id'), 'offer_id'),
              ]
