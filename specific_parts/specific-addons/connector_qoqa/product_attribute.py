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

from openerp.addons.connector.connector import ConnectorUnit
from .backend import qoqa



@qoqa
class ProductAttribute(ConnectorUnit):
    """ Build a dictionary of values for a product or a template from an
    attribut set structure"""
    _model_name = ['qoqa.product.product',
                   'qoqa.product.template',
                   ]

    def _get_select_option(self, option, attribute):
        if not option:
            return None
        if attribute.relation_model_id:
            binder = self.get_binder_for_model(option._model._name)
            value = binder.to_backend(option.id, wrap=True)
        else:
            value = option.name
        return value

    def get_values(self, record):
        result = {}
        if not record.attribute_set_id:
            return result
        model_type = record.openerp_id._model._name
        groups = record.attribute_set_id.attribute_group_ids
        attributes = [attribute for group in groups
                      for attribute in group.attribute_ids]
        for attribute in attributes:
            if attribute.model_id.model != model_type:
                continue
            name = attribute.name
            value = record[name]
            if attribute.attribute_type == 'select':
                value = self._get_select_option(value, attribute)
            elif attribute.attribute_type == 'multiselect':
                value = [self._get_select_option(val, attribute)
                         for val in value]
            if name.startswith('x_'):
                name = name[2:]
            result[name] = value
        return result
