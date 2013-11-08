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

import mock

import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from ..product_attribute.exporter import ProductAttribute


class test_product_attributes(common.TransactionCase):
    """ Test the binding of a company.

    It is special because it expect the QoQa IDs to be manually
    setup.
    """

    def setUp(self):
        super(test_product_attributes, self).setUp()
        cr, uid = self.cr, self.uid
        self.backend_id = self.ref('connector_qoqa.qoqa_backend_config')

        self.Set = self.registry('attribute.set')
        self.Group = self.registry('attribute.group')
        self.Attribute = self.registry('attribute.attribute')
        self.Option = self.registry('attribute.option')
        self.Location = self.registry('attribute.location')
        self.QoQaProduct = self.registry('qoqa.product.product')
        self.QoQaTemplate = self.registry('qoqa.product.template')
        template_model_id = self.ref('procurement.model_product_template')
        product_model_id = self.ref('procurement.model_product_product')
        self.set_id = self.Set.create(
            cr, uid, {'name': 'test', 'model_id': product_model_id})
        self.attr_tmpl_char_id = self.Attribute.create(
            cr, uid,
            {'name': 'x_test_tmpl_char',
             'field_description': 'Template Char',
             'attribute_type': 'char',
             'model_id': template_model_id})
        self.attr_char_id = self.Attribute.create(
            cr, uid,
            {'name': 'x_test_char',
             'field_description': 'Char',
             'attribute_type': 'char',
             'model_id': product_model_id})
        self.attr_select_id = self.Attribute.create(
            cr, uid,
            {'name': 'x_test_select',
             'field_description': 'Selection',
             'attribute_type': 'select',
             'model_id': product_model_id})
        self.option1_id = self.Option.create(
            cr, uid,
            {'name': 'Option 1',
             'attribute_id': self.attr_select_id})
        self.attr_multiselect_id = self.Attribute.create(
            cr, uid,
            {'name': 'x_test_multiselect',
             'field_description': 'Multi-Selection',
             'attribute_type': 'multiselect',
             'model_id': product_model_id})
        self.option2_id = self.Option.create(
            cr, uid,
            {'name': 'Option 2',
             'attribute_id': self.attr_multiselect_id})
        self.option3_id = self.Option.create(
            cr, uid,
            {'name': 'Option 3',
             'attribute_id': self.attr_multiselect_id})
        self.group_id = self.Group.create(
            cr, uid,
            {'name': 'Test Group',
             'attribute_set_id': self.set_id,
             'model_id': product_model_id})
        self.loc1_id = self.Location.create(
            cr, uid, {'attribute_group_id': self.group_id,
                      'attribute_id': self.attr_tmpl_char_id})
        self.loc2_id = self.Location.create(
            cr, uid, {'attribute_group_id': self.group_id,
                      'attribute_id': self.attr_char_id})
        self.loc3_id = self.Location.create(
            cr, uid, {'attribute_group_id': self.group_id,
                      'attribute_id': self.attr_select_id})
        self.loc4_id = self.Location.create(
            cr, uid, {'attribute_group_id': self.group_id,
                      'attribute_id': self.attr_multiselect_id})

        product_id = self.QoQaProduct.create(
            cr, uid,
            {'name': 'Test Product',
             'backend_id': self.backend_id,
             'attribute_set_id': self.set_id,
             'x_test_tmpl_char': 'x_test_tmpl_char',
             'x_test_char': 'x_test_char',
             'x_test_select': self.option1_id,
             'x_test_multiselect': [(6, 0, [self.option2_id,
                                            self.option3_id])]},
            context={'connector_no_export': True})
        self.product = self.QoQaProduct.browse(cr, uid, product_id)
        self.QoQaTemplate.create(
            cr, uid, {'backend_id': self.backend_id,
                      'openerp_id': self.product.product_tmpl_id.id},
            context={'connector_no_export': True})
        self.session = ConnectorSession(cr, uid)

    def test_template_attributes(self):
        """ Get values of attributes from a template only """
        environment = get_environment(self.session, 'product.template',
                                      self.backend_id)
        qtemplate = self.product.product_tmpl_id.qoqa_bind_ids[0]
        attrs = ProductAttribute(environment)
        values = attrs.get_values(qtemplate)
        self.assertEquals(values, {'test_tmpl_char': 'x_test_tmpl_char'})

    def test_product_attributes(self):
        """ Get values of attributes from a variant only """
        environment = get_environment(self.session, 'product.product',
                                      self.backend_id)
        attrs = ProductAttribute(environment)
        values = attrs.get_values(self.product)
        self.assertEquals(values,
                          {u'test_char': u'x_test_char',
                           u'test_select': u'Option 1',
                           u'test_multiselect': [u'Option 2', u'Option 3']})

    def tearDown(self):
        cr, uid = self.cr, self.uid
        option_ids = [self.option1_id, self.option2_id, self.option3_id]
        self.Option.unlink(cr, uid, option_ids)
        attr_ids = [self.attr_tmpl_char_id,
                    self.attr_char_id,
                    self.attr_select_id,
                    self.attr_multiselect_id]
        attributes = self.Attribute.browse(cr, uid, attr_ids)
        Fields = self.registry('ir.model.fields')
        Fields.unlink(cr, uid, [attr.field_id.id for attr in attributes])
        location_ids = [self.loc1_id, self.loc2_id, self.loc3_id, self.loc4_id]
        self.Location.unlink(cr, uid, location_ids)
        self.Group.unlink(cr, uid, self.group_id)
        self.Attribute.unlink(cr, uid, attr_ids)
        self.Set.unlink(cr, uid, self.set_id)
        super(test_product_attributes, self).tearDown()

"""
DELETE FROM attribute_option
WHERE attribute_id IN (SELECT id FROM attribute_attribute
                       WHERE field_id IN (SELECT id FROM ir_model_fields
                                          WHERE name IN ('x_test_tmpl_char', 'x_test_char',
                                                         'x_test_select', 'x_test_multiselect')
));

DELETE FROM attribute_location
WHERE attribute_id IN (SELECT id FROM attribute_attribute
                       WHERE field_id IN (SELECT id FROM ir_model_fields
                                          WHERE name IN ('x_test_tmpl_char', 'x_test_char',
                                                         'x_test_select', 'x_test_multiselect')
));

DELETE FROM attribute_attribute
WHERE field_id IN (SELECT id FROM ir_model_fields
                   WHERE name IN ('x_test_tmpl_char', 'x_test_char',
                                  'x_test_select', 'x_test_multiselect'));


DELETE FROM attribute_group WHERE name = 'Test Group';

DELETE FROM attribute_set WHERE name = 'test';

DELETE FROM ir_model_fields
WHERE name IN ('x_test_tmpl_char', 'x_test_char', 'x_test_select', 'x_test_multiselect');
"""
