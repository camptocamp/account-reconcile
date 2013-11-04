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

from openerp.addons.connector.unit import mapper


def m2o_to_backend(field, binding=None):
    """ A modifier intended to be used on the ``direct`` mappings.

    For a many2one, get the ID on the backend and returns it.

    When the field's relation is not a binding (i.e. it does not point to
    something like ``magento.*``), the binding model needs to be provided
    in the ``binding`` keyword argument.

    QoQa always expects None for NULL relations, so we replace the False
    values with None.

    Example::

        direct = [(m2o_to_backend('country_id', binding='magento.res.country'),
                   'country'),
                  (m2o_to_backend('magento_country_id'), 'country')]

    :param field: name of the source field in the record
    :param binding: name of the binding model is the relation is not a binding
    """
    return mapper.none(mapper.m2o_to_backend(field, binding=binding))


def ifmissing(field, value):
    """ A modifier intended to be used on the ``direct`` mappings.

    When the input value is False-ish (False, None, ''), it set the
    ``value`` instead. It can be used for instance to replace a
    missing name by 'Unknown'.

    Example::

        direct = [(ifmissing('name', value='Unknown'), 'name')]

    :param field: name of the source field in the record
    :param value: default value to put when the source value is False-ish
    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return value
        return value
    return modifier
