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

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,
                                                  )
from openerp.addons.connector.exception import MappingError
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        TranslationImporter,
                                        )
from ..product_attribute.importer import ProductAttribute
from ..unit.mapper import ifmissing, iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class TemplateBatchImport(DelayedBatchImport):
    """ Import the QoQa Product Templates.

    For every product in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['qoqa.product.template']


@qoqa
class TemplateImport(QoQaImportSynchronizer):
    _model_name = ['qoqa.product.template']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.qoqa_record
        # import related categories
        # binder = self.get_binder_for_model('magento.product.category')
        # for mag_category_id in record['categories']:
        #     if binder.to_openerp(mag_category_id) is None:
        #         importer = self.get_connector_unit_for_model(
        #             MagentoImportSynchronizer,
        #             model='magento.product.category')
        #         importer.run(mag_category_id)

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        translation_importer = self.get_connector_unit_for_model(
            TranslationImporter)
        translation_importer.run(self.qoqa_record, binding_id)


@qoqa
class TemplateImportMapper(ImportMapper):
    _model_name = 'qoqa.product.template'

    translatable_fields = [
        (ifmissing('name', 'Unknown'), 'name'),
        (ifmissing('description', ''), 'description_sale'),
    ]

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ]

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(TemplateImportMapper, self).__init__(environment)
        self.lang = self.backend_record.default_lang_id

    @only_create
    @mapping
    def type(self, record):
        return {'type': 'product'}

    @mapping
    def attributes(self, record):
        """ Extract the attributes from the record.

        It takes all the attributes. For the translatable ones,
        """
        attr = self.get_connector_unit_for_model(ProductAttribute)
        translatable = None
        if self.lang != self.backend_record.default_lang_id:
            translatable = True  # filter only translatable attributes
        return attr.get_values(record, self.lang, translatable=translatable)

    @mapping
    def from_translations(self, record):
        """ The translatable fields are only provided in
        a 'translations' dict, we take the translation
        for the main record in OpenERP.
        """
        binder = self.get_binder_for_model('res.lang')
        qoqa_lang_id = binder.to_backend(self.lang.id, wrap=True)
        main = next((tr for tr in record['translations']
                     if str(tr['language_id']) == str(qoqa_lang_id)), {})
        values = {}
        for source, target in self.translatable_fields:
            values[target] = self._map_direct(main, source, target)
        return values

    # TODO: product_metas (only for the import -> for the wine reports)
