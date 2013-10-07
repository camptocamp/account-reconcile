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


class qoqa_deal_position_variant(orm.Model):
    _inherit = 'qoqa.deal.position.variant'

    _columns = {
        'backend_id': fields.related(
            'position_id', 'deal_id', 'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa'),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }


@on_record_create(model_names='qoqa.deal.position.variant')
@on_record_write(model_names='qoqa.deal.position.variant')
def delay_export(session, model_name, record_id, fields=None):
    # reduce the priority so the deals and positions should be exported before
    consumer.delay_export(session, model_name, record_id,
                          fields=fields, priority=20)


@on_record_unlink(model_names='qoqa.deal.position.variant')
def delay_unlink(session, model_name, record_id):
    consumer.delay_unlink(session, model_name, record_id)


@qoqa
class DealPositionVariantDeleteSynchronizer(QoQaDeleteSynchronizer):
    """ Deal deleter for QoQa """
    _model_name = ['qoqa.deal.position.variant']


@qoqa
class DealPositionVariantExporter(QoQaExporter):
    _model_name = ['qoqa.deal.position.variant']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        binding = self.binding_record
        self._export_dependency(binding.position_id, 'qoqa.deal.position')
        self._export_dependency(binding.product_id, 'qoqa.product.product')


@qoqa
class DealPositionVariantAdapter(QoQaAdapter):
    _model_name = 'qoqa.deal.position.variant'
    _endpoint = 'variations'


@qoqa
class DealPositionVariantExportMapper(ExportMapper):
    _model_name = 'qoqa.deal.position.variant'

    direct = [('product_id', 'product_id'),
              ('quantity', 'quantity'),
              ('position_id', 'position_id'),
              ]
