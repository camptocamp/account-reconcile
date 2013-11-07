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

from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.connector import ConnectorUnit
from ..backend import qoqa


class ProductAttribute(ConnectorUnit):
    """ For a product's template or variant, search all the
    attributes and returns a dict ready to be used by the Mapper.
    """
    _model_name = None

    attr_model = None  # used to filter the attributes

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(ProductAttribute, self).__init__(environment)
        assert self.attr_model, "attr_model must be set"

    def _get_select_option(self, value, attribute):
        if not value:
            return False
        if attribute.relation_model_id:
            model_name = attribute.relation_model_id.model
            model = self.session.pool.get(model_name)
            binder = self.get_binder_for_model(model._name)
            return binder.to_openerp(value, unwrap=True)

        binder = self.get_binder_for_model('attribute.option')
        return binder.to_openerp(value.id, unwrap=True)

    def _attribute_set_id(self, record):
        """ Try to find the appropriate attribute set for the template.

        In QoQa, there is no attribute set idea. We try to infer it
        from the record.

        """
        data_obj = self.session.pool.get('ir.model.data')
        mod = 'qoqa_base_data'
        # metas are only used for the wine products
        if record['product_metas']:
            xmlid = 'set_wine'
        else:
            xmlid = 'set_general'
        cr, uid = self.session.cr, self.session.uid
        try:
            __, res_id = data_obj.get_object_reference(cr, uid, mod, xmlid)
        except ValueError:
            raise MappingError('Attribute set %s is missing.' %
                               ('.'.join((mod, xmlid))))

        return res_id

    def get_values(self, record, language, translatable=None):
        """ Extract the attribute values from the backend's record.

        :param record: backend's record
        :type record: dict
        :param language: browse_record of the language for which we extract
                            the values
        :type language: browse_record

        """
        result = {}
        attr_set_id = self._attribute_set_id(record)
        attr_set = self.session.browse('attribute.set', attr_set_id)
        groups = attr_set.attribute_group_ids
        locations = [attribute for group in groups
                     for attribute in group.attribute_ids]

        attr_binder = self.get_binder_for_model('attribute.attribute')

        lang_binder = self.get_binder_for_model('res.lang')
        qoqa_lang_id = lang_binder.to_backend(language.id, wrap=True)
        for location in locations:
            attribute = location.attribute_id
            if attribute.model_id.model != self.attr_model:
                continue
            if (translatable is not None and
                    attribute.translate != translatable):
                continue
            qoqa_name = attr_binder.to_backend(attribute.id)
            rec_tr = next((tr for tr in record['translations']
                           if str(tr['language_id']) == str(qoqa_lang_id)),
                          {})
            value = rec_tr.get(qoqa_name)
            if value is None:
                value = record.get(qoqa_name)

            if attribute.attribute_type == 'select':
                value = self._get_select_option(value, attribute)
            elif attribute.attribute_type == 'multiselect':
                value = [self._get_select_option(val, attribute)
                         for val in value]

            result[attribute.name] = value

        result['attribute_set_id'] = attr_set_id
        return result


@qoqa
class VariantProductAttribute(ProductAttribute):
    """ For a product's variant, search all the
    attributes and returns a dict ready to be used by the Mapper.
    """
    _model_name = 'qoqa.product.product'

    attr_model = 'product.product'  # used to filter the attributes

    def _attribute_set_id(self, record):
        """ Try to find the appropriate attribute set for the template.

        In QoQa, there is no attribute set idea. We try to infer it
        from the record.

        """
        qoqa_tmpl_id = record['product_id']
        tmpl_binder = self.get_binder_for_model('qoqa.product.template')
        qoqa_product_id = record['product_id']
        tmpl_id = tmpl_binder.to_openerp(qoqa_product_id, unwrap=True)
        assert tmpl_id is not None, \
               ("product_id %s should have been imported in "
                "VariantImport._import_dependencies" % record['product_id'])
        tmpl = self.session.browse('product.template', tmpl_id)
        return tmpl.attribute_set_id.id


@qoqa
class TemplateProductAttribute(ProductAttribute):
    """ For a product's template, search all the
    attributes and returns a dict ready to be used by the Mapper.
    """
    _model_name = 'qoqa.product.template'

    attr_model = 'product.template'  # used to filter the attributes

    def _attribute_set_id(self, record):
        """ Try to find the appropriate attribute set for the template.

        In QoQa, there is no attribute set idea. We try to infer it
        from the record.

        """
        data_obj = self.session.pool.get('ir.model.data')
        mod = 'qoqa_base_data'
        # metas are only used for the wine products
        if record['product_metas']:
            xmlid = 'set_wine'
        else:
            xmlid = 'set_general'
        cr, uid = self.session.cr, self.session.uid
        try:
            __, res_id = data_obj.get_object_reference(cr, uid, mod, xmlid)
        except ValueError:
            raise MappingError('Attribute set %s is missing.' %
                               ('.'.join((mod, xmlid))))

        return res_id
