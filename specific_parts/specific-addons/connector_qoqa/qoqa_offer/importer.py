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

from __future__ import division

from datetime import datetime

from openerp.addons.connector.unit.mapper import (mapping,
                                                  backend_to_m2o,
                                                  ImportMapper)
from openerp.addons.connector.exception import MappingError
from ..backend import qoqa
from ..unit.import_synchronizer import (QoQaImportSynchronizer,
                                        TranslationImporter,
                                        )
from ..unit.mapper import ifmissing
from ..exception import QoQaError


@qoqa
class QoQaOfferImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.offer'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['shop_id'], 'qoqa.shop')

    def _import(self, binding_id):
        """ Use the user from the shop's company for the import

        Allowing the records rules to be applied.

        """
        qshop_binder = self.get_binder_for_model('qoqa.shop')
        qshop_id = qshop_binder.to_openerp(self.qoqa_record['shop_id'])
        qshop = self.session.browse('qoqa.shop', qshop_id)
        user = qshop.company_id.connector_user_id
        if not user:
            raise QoQaError('No connector user configured for company %s' %
                            qshop.company_id.name)
        with self.session.change_user(user.id):
            super(QoQaOfferImport, self)._import(binding_id)

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        translation_importer = self.get_connector_unit_for_model(
            TranslationImporter)
        translation_importer.run(self.qoqa_record, binding_id)


@qoqa
class QoQaOfferImportMapper(ImportMapper):
    _model_name = 'qoqa.offer'

    direct = [(ifmissing('notes', '<p></p>'), 'note'),
              (backend_to_m2o('language_id', binding='res.lang'), 'lang_id'),
              (backend_to_m2o('shop_id'), 'qoqa_shop_id'),
              (backend_to_m2o('shipper_service_id',
                              binding='qoqa.shipper.service'),
               'carrier_id'),
              (backend_to_m2o('shipper_rate_id', binding='qoqa.shipper.rate'),
               'shipper_rate_id'),
              ('id', 'ref'),
              ('is_active', 'active'),
              ]

    translatable_fields = [
        (ifmissing('title', '...?'), 'title'),
        (ifmissing('content', ''), 'description'),
    ]

    @mapping
    def pricelist(self, record):
        binder = self.get_binder_for_model('res.currency')
        currency_id = binder.to_openerp(record['currency_id'], unwrap=True)
        pricelist_ids = self.session.search(
            'product.pricelist', [('type', '=', 'sale'),
                                  ('currency_id', '=', currency_id)])
        if not pricelist_ids:
            raise MappingError('No pricelist for currency %d' % currency_id)
        return {'pricelist_id': pricelist_ids[0]}

    @staticmethod
    def _qoqa_datetime(timestamp):
        """ The start and end dates of an offer are special:

        We want them to be displayed at the same time to the user
        whatever their timezone is.  The date / time should be displayed
        in the QoQa TZ, that is: Europe/Zurich.
        So we do not store it as a normal timestamp, but as separate
        date and time thus they are not stored in UTC. We also keep
        them at the QoQa's local time.

        """
        dt_str = timestamp[0:10]
        time_str = timestamp[11:19]
        time = datetime.strptime(time_str, '%H:%M:%S')
        time_f = time.hour + (time.minute / 60) + (time.second / 3600)
        return dt_str, time_f

    @mapping
    def start_at(self, record):
        dt, time = self._qoqa_datetime(record['start_at'])
        return {'date_begin': dt, 'time_begin': time}

    @mapping
    def stop_at(self, record):
        dt, time = self._qoqa_datetime(record['stop_at'])
        return {'date_end': dt, 'time_end': time}

    @mapping
    def from_translations(self, record):
        """ The translatable fields are only provided in
        a 'translations' dict, we take the translation
        for the main record in OpenERP.
        """
        binder = self.get_binder_for_model('res.lang')
        lang = self.options.lang or self.backend_record.default_lang_id
        qoqa_lang_id = binder.to_backend(lang.id, wrap=True)
        main = next((tr for tr in record['translations']
                     if str(tr['language_id']) == str(qoqa_lang_id)), {})
        values = {}
        for source, target in self.translatable_fields:
            values[target] = self._map_direct(main, source, target)
        return values
