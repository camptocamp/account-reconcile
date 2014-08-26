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

from openerp.addons.product.product import check_ean
from openerp.addons.connector.unit.mapper import (mapping,
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        TranslationImporter,
                                        )
from ..product_attribute.importer import ProductAttribute
from ..product_template.importer import TemplateVariantImportMapper
from ..unit.mapper import iso8601_to_utc, qoqafloat

_logger = logging.getLogger(__name__)


@qoqa
class VariantBatchImport(DelayedBatchImport):
    """ Import the QoQa Product Variants.

    For every product in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['qoqa.product.product']


@qoqa
class VariantImport(QoQaImportSynchronizer):
    _model_name = ['qoqa.product.product']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['product_id'], 'qoqa.product.template')

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        translation_importer = self.get_connector_unit_for_model(
            TranslationImporter)
        translation_importer.run(self.qoqa_record, binding_id,
                                 mapper=VariantImportMapper)

    @property
    def mapper(self):
        if self._mapper is None:
            env = self.environment
            self._mapper = env.get_connector_unit(VariantImportMapper)
        return self._mapper


@qoqa
class VariantImportMapper(ImportMapper):
    _model_name = 'qoqa.product.product'

    translatable_fields = [
        ('name', 'variants'),
    ]

    direct = [
        (iso8601_to_utc('created_at'), 'created_at'),
        (iso8601_to_utc('updated_at'), 'updated_at'),
        ('sku', 'default_code'),
        (backend_to_m2o('product_id', binding='qoqa.product.template'),
         'product_tmpl_id'),
        ('warranty', 'warranty'),
        (qoqafloat('cost_price'), 'standard_price'),
    ]

    @mapping
    def ean(self, record):
        if not record['ean']:
            return
        ean13 = str(record['ean'])
        if check_ean(ean13):
            return {'ean13': ean13}

    @mapping
    def attributes(self, record):
        """ Extract the attributes from the record.

        It takes all the attributes. For the translatable ones,
        """
        attr = self.get_connector_unit_for_model(ProductAttribute)
        translatable = None
        lang = self.options.lang or self.backend_record.default_lang_id
        if lang != self.backend_record.default_lang_id:
            translatable = True  # filter only translatable attributes
        return attr.get_values(record, lang, translatable=translatable)

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

    @mapping
    def common_with_template(self, record):
        """ Share some mappings with the template """
        mapper = self.get_connector_unit_for_model(
            TemplateVariantImportMapper)
        map_record = mapper.map_record(record)
        return map_record.values(**self.options)
