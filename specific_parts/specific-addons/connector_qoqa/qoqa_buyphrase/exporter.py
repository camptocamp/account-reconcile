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
                                                  ExportMapper)
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )
from ..backend import qoqa
from .. import consumer
from ..unit.export_synchronizer import QoQaExporter, Translations
from ..unit.mapper import m2o_to_backend


@on_record_create(model_names='qoqa.buyphrase')
@on_record_write(model_names='qoqa.buyphrase')
def delay_export(session, model_name, record_id, fields=None):
    consumer.delay_export(session, model_name, record_id,
                          fields=fields)


@qoqa
class BuyphraseExporter(QoQaExporter):
    _model_name = ['qoqa.buyphrase']


@qoqa
class BuyphraseExportMapper(ExportMapper):
    _model_name = 'qoqa.buyphrase'

    direct = [('active', 'is_active'),
              ('action', 'action'),
              (m2o_to_backend('qoqa_shop_id'), 'shop_id'),
              ]

    translatable_fields = [
        ('name', 'buy_text'),
        ('description', 'definition'),
    ]

    @mapping
    def translations(self, record):
        """ Map all the translatable values

        Translatable fields for QoQa are sent in a `translations`
        key and are not sent in the main record.
        """
        fields = self.translatable_fields
        trans = self.get_connector_unit_for_model(Translations)
        return trans.get_translations(record, normal_fields=fields)
