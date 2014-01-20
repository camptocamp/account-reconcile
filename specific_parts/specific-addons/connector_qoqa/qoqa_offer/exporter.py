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

from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )
from ..backend import qoqa
from .. import consumer
from ..unit.export_synchronizer import QoQaExporter, Translations
from ..unit.mapper import m2o_to_backend
from ..connector import utc_datetime_to_iso8601
from ..qoqa_offer_position.exporter import delay_export as position_delay_export


@on_record_create(model_names='qoqa.offer')
@on_record_write(model_names='qoqa.offer')
def delay_export(session, model_name, record_id, vals):
    fields = vals.keys()
    if fields is not None and 'stock_bias' in fields:
        # particular case: stock_bias is stored in the positions on
        # the QoQa backend, delay export of all positions
        for position in session.browse(model_name, record_id).position_ids:
            position_delay_export(session, 'qoqa.offer.position',
                                  position.id, fields=['stock_bias'])
        # just skip the export of the offer if only the bias has been
        # modified
        if fields == ['stock_bias']:
            return
    # High priority because we want the changes to be quick
    # so they are displayed asap to the customer.
    consumer.delay_export(session, model_name, record_id,
                          fields=fields, priority=4)


@qoqa
class OfferExporter(QoQaExporter):
    _model_name = ['qoqa.offer']


@qoqa
class OfferExportMapper(ExportMapper):
    _model_name = 'qoqa.offer'

    translatable_fields = [
        ('title', 'title'),
        ('description', 'content'),
    ]

    direct = [
        ('note', 'notes'),
        (m2o_to_backend('qoqa_shop_id'), 'shop_id'),
        (m2o_to_backend('lang_id'), 'language_id'),
        (m2o_to_backend('carrier_id', binding='qoqa.shipper.service'),
         'shipper_service_id'),
        (m2o_to_backend('shipper_rate_id', binding='qoqa.shipper.rate'),
         'shipper_rate_id'),
        ('ref', 'id'),
        ('active', 'is_active'),
    ]

    @staticmethod
    def _qoqa_datetime(date, hours):
        dt = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        dt += timedelta(hours=hours)
        return utc_datetime_to_iso8601(dt)

    @mapping
    def start_at(self, record):
        start = self._qoqa_datetime(record.date_begin, record.time_begin)
        return {'start_at': start}

    @mapping
    def stop_at(self, record):
        stop = self._qoqa_datetime(record.date_end, record.time_end)
        return {'stop_at': stop}

    @mapping
    def currency(self, record):
        currency = record.pricelist_id.currency_id
        binder = self.get_binder_for_model('res.currency')
        qoqa_ccy_id = binder.to_backend(currency.id, wrap=True)
        return {'currency_id': qoqa_ccy_id}

    @mapping
    def translations(self, record):
        """ Map all the translatable values

        Translatable fields for QoQa are sent in a `translations`
        key and are not sent in the main record.
        """
        fields = self.translatable_fields
        trans = self.get_connector_unit_for_model(Translations)
        return trans.get_translations(record, normal_fields=fields)
