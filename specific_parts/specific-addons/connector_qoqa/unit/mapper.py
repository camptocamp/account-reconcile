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

from __future__ import division

from datetime import datetime
from openerp.tools.misc import (DEFAULT_SERVER_DATETIME_FORMAT,
                                DEFAULT_SERVER_DATE_FORMAT,
                                )
from openerp.addons.connector.unit import mapper
from ..connector import iso8601_to_utc_datetime, utc_datetime_to_iso8601


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
    """ A modifier intended to be used on the ``direct`` mappings.

    A QoQa date is formatted using the ISO 8601 format.
    Convert an ISO 8601 timestamp to an UTC datetime as string
    as expected by OpenERP.

    Example: 2013-11-04T13:52:01+0100 -> 2013-11-04 12:52:01

    Usage::

        direct = [(iso8601_to_utc('name', value='Unknown'), 'name')]

    :param field: name of the source field in the record

    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return False
        utc_date = iso8601_to_utc_datetime(value)
        return utc_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    return modifier


def date_to_iso8601(field):
    """ A modifier intended to be used on the ``direct`` mappings.

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
            fmt = DEFAULT_SERVER_DATE_FORMAT
        else:
            fmt = DEFAULT_SERVER_DATETIME_FORMAT
        dt = datetime.strptime(value, fmt)
        utc_date = utc_datetime_to_iso8601(dt)
        return utc_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    return modifier


def qoqafloat(field):
    """ A modifier intended to be used on the ``direct`` mappings for
    importers.

    QoQa provides the float values multiplied by 100.
    Example: 33.00 is represented as 3300 on the API.

    Usage::

        direct = [(qoqafloat('unit_price'), 'unit_price')]

    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = record.get(field) or 0
        return float(value) / 100
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


def floatqoqa(field):
    """ A modifier intended to be used on the ``direct`` mappings for
    exporters.

    QoQa provides the float values multiplied by 100.
    Example: 33.00 is represented as 3300 on the API.

    Usage::

        direct = [(floatqoqa('unit_price'), 'unit_price')]

    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = record[field] or 0
        return float(value) * 100
    return modifier
