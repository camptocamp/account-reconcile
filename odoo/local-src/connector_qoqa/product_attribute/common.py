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

from openerp.osv import orm, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class attribute_attribute(orm.Model):
    _inherit = 'attribute.attribute'
    _columns = {
        'qoqa_id': fields.char('Name of the field on QoQa',
                               help="If empty, it uses the name of the "
                                    "attribute without the x_ prefix",
                               select=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
        })
        return super(attribute_attribute, self).copy_data(
            cr, uid, id, default=default, context=context)


class attribute_option(orm.Model):
    _inherit = 'attribute.option'
    _columns = {
        'qoqa_id': fields.char('Value of the option on QoQa',
                               help="If empty, it uses the current value.\n"
                                    "Not applicable for attributes with a "
                                    "relation."),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
        })
        return super(attribute_option, self).copy_data(
            cr, uid, id, default=default, context=context)


@qoqa
class AttributeBinder(QoQaDirectBinder):
    _model_name = 'attribute.attribute'

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: No effect in the direct binding
        :return: ID of the record in OpenERP
                 or None if the external_id is not mapped
        :rtype: int
        """
        # attribute name is `qoqa_id`
        # or is the name of the attribute or is the name of the attribute
        # which is a custom field (prefixed with x_)
        binding_ids = self.session.search(
            self.model._name,
            ['|', '|', ('qoqa_id', '=', str(external_id)),
                       ('name', '=', str(external_id)),
                       ('name', '=', 'x_' + str(external_id))])

        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        return binding_ids[0]

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        Wrap is not applicable for this binder because the binded record
        is the same than the binding record.

        :param binding_id: OpenERP ID for which we want the external id
        :param wrap: if True, the value passed in binding_id is the ID of the
                     binded record, not the binding record.
        :return: backend identifier of the record
        """
        attribute = self.session.browse(self.model._name, binding_id)
        assert attribute
        qoqa_name = attribute.qoqa_id
        if not qoqa_name:
            if attribute.name.startswith('x_'):
                qoqa_name = attribute.name[2:]
            else:
                qoqa_name = attribute.name
        if not qoqa_name:  # prefer None over False
            return None
        return qoqa_name

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        raise TypeError('%s cannot be synchronized' % self._model_name)


@qoqa
class AttributeOptionBinder(QoQaDirectBinder):
    _model_name = 'attribute.option'

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: No effect in the direct binding
        :return: ID of the record in OpenERP
                 or None if the external_id is not mapped
        :rtype: int
        """
        binding_ids = self.session.search(
            self.model._name,
            [('qoqa_id', '=', str(external_id))])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        return binding_ids[0]

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        Wrap is not applicable for this binder because the binded record
        is the same than the binding record.

        :param binding_id: OpenERP ID for which we want the external id
        :param wrap: if True, the value passed in binding_id is the ID of the
                     binded record, not the binding record.
        :return: backend identifier of the record
        """
        option = self.session.browse(self.model._name, binding_id)
        assert option
        qoqa_value = option.qoqa_id or option.name
        if not qoqa_value:  # prefer None over False
            return None
        return qoqa_value

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        raise TypeError('%s cannot be synchronized' % self._model_name)


@qoqa
class WineBottleBinder(QoQaDirectBinder):
    _model_name = 'wine.bottle'

    """ This mapper is to map the bottle's volume to 'capacity' """

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: No effect in the direct binding
        :return: ID of the record in OpenERP
                 or None if the external_id is not mapped
        :rtype: int

        Not used in wine.bottle.
        """
        return None

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        Wrap is not applicable for this binder because the binded record
        is the same than the binding record.

        :param binding_id: OpenERP ID for which we want the external id
        :param wrap: if True, the value passed in binding_id is the ID of the
                     binded record, not the binding record.
        :return: backend identifier of the record
        """
        bottle = self.session.browse(self.model._name, binding_id)
        assert bottle
        qoqa_value = bottle.volume
        if not qoqa_value:  # prefer None over False
            return None
        return qoqa_value
