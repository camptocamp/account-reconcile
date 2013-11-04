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
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from openerp.addons.connector.exception import MappingError
from ..backend import qoqa
from ..unit.import_synchronizer import (FromDateDelayBatchImport,
                                        QoQaImportSynchronizer,
                                        TranslationImporter,
                                        )
from ..product_attribute.importer import ProductAttribute
from ..unit.mapper import ifmissing

_logger = logging.getLogger(__name__)


@qoqa
class VariantBatchImport(FromDateDelayBatchImport):
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
        record = self.qoqa_record
        # import related template if missing
        tmpl_binder = self.get_binder_for_model('qoqa.product.template')
        qoqa_product_id = record['product_id']
        if tmpl_binder.to_openerp(qoqa_product_id) is None:
            importer = self.get_connector_unit_for_model(
                QoQaImportSynchronizer,
                model='qoqa.product.template')
            importer.run(qoqa_product_id)

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        translation_importer = self.get_connector_unit_for_model(
            TranslationImporter)
        translation_importer.run(self.qoqa_record, binding_id)


@qoqa
class VariantImportMapper(ImportMapper):
    _model_name = 'qoqa.product.product'

    translatable_fields = [
        (ifmissing('name', 'Unknown'), 'variants'),
    ]

    direct = [
        ('created_at', 'created_at'),
        ('updated_at', 'updated_at'),
        ('sku', 'default_code'),
        ('ean', 'ean13'),
        (backend_to_m2o('product_id', binding='qoqa.product.template'),
        'product_tmpl_id'),
    ]

    # TODO: warranty_id

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(VariantImportMapper, self).__init__(environment)
        self.lang = self.backend_record.default_lang_id

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

"""

{u'created_at': u'2013-10-11T10:06:27+0200',
 u'id': 5365,
 u'product_metas': [],
 u'translations': [{u'brand': u'Juicepresso',
                    u'description': u'<p style="margin-top: 10px; margin-right: 0px; margin-bottom: 10px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; "><strong style="font-style: inherit; font-weight: bold; margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Caract&eacute;ristiques techniques :</strong></p>\r\n\r\n<ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 30px; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Obtient jusqu&acute;&agrave; 6x plus de vitamines qu&acute;une centrifugeuse classique, gr&acirc;ce &agrave; son syst&egrave;me de s&eacute;paration par pression &agrave; froid de la pulpe et sa rotation lente, vous conserverez un maximum de vitamines et obtiendrez jusqu&acute;&agrave; 2 fois plus de jus qu&acute;une centrifugeuse</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Avec 30dB le Juicepresso est tr&egrave;s silencieux et parfait pour effectuer une pr&eacute;paration culinaire sans contrainte sonore</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Nettoyage&nbsp;facile par simple rincage &agrave; l&acute;eau par la goulotte vous &eacute;vite de d&eacute;monter tout l&acute;appareil. Apr&egrave;s rincage vous pouvez travailler avec des saveurs nouvelles sans pour autant les m&eacute;langer avec le go&ucirc;t pr&eacute;c&eacute;dent. A la fin de l&acute;utilisation, le Juicepresso se demonte facilement et se nettoie sous l&acute;eau clair. Un accessoire (brosse) vous permet un nettoyage en profondeur avant son prochain emploi</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">R&eacute;unit les services d&#39;un presse agrume, machine &agrave; jus, appareil &agrave; jus de fruits, presse oranges, centrifugeuse etc.&nbsp;</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Nettoyage facile &agrave; l&#39;eau</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Sans Biphenol A</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Consommation : 150Watt</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Vitesse : 40 / tours par minute</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Longueur cordon : 1,4m</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Poids : 6,4 kg</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Dimensions : 140 x 194 x 306 mm</li>\r\n\t<li style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; list-style-type: disc; list-style-position: outside; list-style-image: initial; border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; ">Garantie 1 an par le fabricant</li>\r\n</ul>\r\n',
                    u'highlights': u"Extraction de jus lente pour plus de vitamines\r\nJus de fruits, l\xe9gumes, ...\r\nNettoyage \xe0 l'eau rapide et facile\r\nSeulement 30dB",
                    u'id': 8535,
                    u'language_id': 1,
                    u'name': u'Extracteur de jus CJP-01',
                    u'product_id': 5365}],
 u'updated_at': u'2013-10-13T23:20:01+0200'}
"""
