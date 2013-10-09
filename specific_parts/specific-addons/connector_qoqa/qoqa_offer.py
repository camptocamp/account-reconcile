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


class qoqa_offer(orm.Model):
    _inherit = 'qoqa.offer'

    _columns = {
        'backend_id': fields.related(
            'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa'),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }


@on_record_create(model_names='qoqa.offer')
@on_record_write(model_names='qoqa.offer')
def delay_export(session, model_name, record_id, fields=None):
    consumer.delay_export(session, model_name, record_id, fields=fields)

@on_record_unlink(model_names='qoqa.offer')
def delay_unlink(session, model_name, record_id):
    consumer.delay_unlink(session, model_name, record_id)


@qoqa
class OfferDeleteSynchronizer(QoQaDeleteSynchronizer):
    """ Offer deleter for QoQa """
    _model_name = ['qoqa.offer']


@qoqa
class OfferExporter(QoQaExporter):
    _model_name = ['qoqa.offer']


@qoqa
class OfferAdapter(QoQaAdapter):
    _model_name = 'qoqa.offer'
    _endpoint = 'deal'


@qoqa
class OfferExportMapper(ExportMapper):
    _model_name = 'qoqa.offer'

    direct = [('name', 'title'),
              ('description', 'content'),
              ('date_begin', 'start_at'),
              ('date_end', 'end_at'),
              ]

    @mapping
    def currency(self, record):
        currency = record.pricelist_id.currency_id
        binder = self.get_binder_for_model('res.currency')
        qoqa_ccy_id = binder.to_backend(currency.id, wrap=True)
        return {'currency': qoqa_ccy_id}
