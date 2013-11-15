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

    @only_create
    @mapping
    def product_type(self, record):
        return {'type': 'product'}

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

    @only_create
    @mapping
    def category(self, record):
        sess = self.session
        data_obj = sess.pool['ir.model.data']
        cr, uid = sess.cr, sess.uid
        xmlid = 'qoqa_base_data', 'product_categ_historical'
        __, category_id = data_obj.get_object_reference(cr, uid, *xmlid)
        return {'categ_id': category_id}

    # TODO: product_metas (only for the import -> for the wine reports)
