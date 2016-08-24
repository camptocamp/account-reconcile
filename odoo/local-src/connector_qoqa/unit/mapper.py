# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division

import logging

from openerp import fields, models
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit import mapper
from ..connector import (iso8601_to_utc_datetime,
                         utc_datetime_to_iso8601,
                         iso8601_to_local_date,
                         )

_logger = logging.getLogger(__name__)


class FromDataAttributes(mapper.Mapper):

    @mapper.mapping
    def values_from_attributes(self, record):
        values = {}
        attribute_fields = getattr(self, 'from_data_attributes', [])
        attributes = record.get('data', {}).get('attributes', {})
        for source, target in attribute_fields:
            values[target] = self._map_direct(attributes, source, target)
        return values


class FromAttributes(mapper.Mapper):

    @mapper.mapping
    def values_from_attributes(self, record):
        values = {}
        attribute_fields = getattr(self, 'from_attributes', [])
        attributes = record.get('attributes', {})
        for source, target in attribute_fields:
            values[target] = self._map_direct(attributes, source, target)
        return values


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
        record_val = record.get(field)
        if not record_val:
            return value
        return record_val
    return modifier


def iso8601_to_utc(field):
    """ A modifier intended to be used on the ``direct`` mappings for
    importers.

    A QoQa date is formatted using the ISO 8601 format.
    Convert an ISO 8601 timestamp to an UTC datetime as string
    as expected by OpenERP.

    Example: 2013-11-04T13:52:01+0100 -> 2013-11-04 12:52:01

    Usage::

        direct = [(iso8601_to_utc('name'), 'name')]

    :param field: name of the source field in the record

    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return False
        utc_date = iso8601_to_utc_datetime(value)
        return fields.Datetime.to_string(utc_date)
    return modifier


def iso8601_local_date(field):
    """ A modifier intended to be used on the ``direct`` mappings for
    importers.

    A QoQa date is formatted using the ISO 8601 format.
    Returns the local date from an iso8601 date.

    Keep only the date, when we want to keep only the local date.
    It's safe to extract it directly from the tz-aware timestamp.
    Example with 2014-10-07T00:34:59+0200: we want 2014-10-07 and not
    2014-10-06 that we would have using the timestamp converted to UTC.

    Usage::

        direct = [(iso8601_local_date('name'), 'name')]

    :param field: name of the source field in the record

    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return False
        utc_date = iso8601_to_local_date(value)
        return fields.Date.to_string(utc_date)
    return modifier


def date_to_iso8601(field):
    """ A modifier intended to be used on the ``direct`` mappings for
    exporters.

    Convert dates to the ISO 8601 format.

    Example: 2013-11-04 12:52:01 → 2013-11-04T12:52:01+0000

    When the input is only a date and not a datetime, it fills
    the timestamp with 0.

    Example: 2013-11-04 → 2013-11-04T00:00:00+0000

    Usage::

        direct = [(date_to_iso8601('date'), 'date')]

    :param field: name of the source field in the record

    """
    def modifier(self, record, to_attr):
        value = record[field]
        if not value:
            return False
        if len(value) == 10:
            fmt = fields.Date.to_string
        else:
            fmt = fields.Datetime.to_string
        dt = fmt(value)
        return utc_datetime_to_iso8601(dt)
    return modifier


def strformat(field, format_string):
    """ A modifier intended to be used on the ``direct`` mappings.

    Format a value given a custom format as expected by ``string.format()``.

    Usage::

        direct = [(format('id', '{0:03d}'), 'name')]

    :param field: name of the source field in the record
    :param format_string: format as expected by string.format()
    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return None
        return format_string.format(value)
    return modifier


def follow_dict_path(field):
    """A modifier intended to be used on ``direct`` mappings.

    'Follows' children keys in dictionaries
    If a key is missing along the path, ``None`` is returned.

    Examples:
        Assuming a dict `{'a': {'b': 1}}

        direct = [
            (follow_dict_path('a.b'), 'cat')]

        Then 'cat' will be 1.

    :param field: field "path", using dots for subkeys
    """
    def modifier(self, record, to_attr):
        attrs = field.split('.')
        value = record
        for attr in attrs:
            value = value.get(attr)
            if not value:
                break
        return value
    return modifier


# can be replaced by the core one once
# https://github.com/OCA/connector/pull/194 is merged
def backend_to_m2o(field, binding=None):
    """ A modifier intended to be used on the ``direct`` mappings.

    For a field from a backend which is an ID, search the corresponding
    binding in OpenERP and returns its ID.

    When the field's relation is not a binding (i.e. it does not point to
    something like ``magento.*``), the binding model needs to be provided
    in the ``binding`` keyword argument.

    Example::

        direct = [(backend_to_m2o('country', binding='magento.res.country'),
                   'country_id'),
                  (backend_to_m2o('country'), 'magento_country_id')]

    :param field: name of the source field in the record
    :param binding: name of the binding model is the relation is not a binding
    """
    def modifier(self, record, to_attr):
        if not record[field]:
            return False
        column = self.model._fields[to_attr]
        if column.type != 'many2one':
            raise ValueError('The column %s should be a Many2one, got %s' %
                             (to_attr, type(column)))
        rel_id = record[field]
        if binding is None:
            binding_model = column.comodel_name
        else:
            binding_model = binding
        binder = self.binder_for(binding_model)
        # if we want the normal record, not a binding,
        # we ask to the binder to unwrap the binding
        unwrap = bool(binding)
        with self.session.change_context(active_test=False):
            record = binder.to_openerp(rel_id, unwrap=unwrap)
        if not record:
            raise MappingError("Can not find an existing %s for external "
                               "record %s %s unwrapping" %
                               (binding_model, rel_id,
                                'with' if unwrap else 'without'))
        if isinstance(record, models.BaseModel):
            return record.id
        else:
            _logger.debug(
                'Binder for %s returned an id, '
                'returning a record should be preferred.', binding_model
            )
            return record
    return modifier
