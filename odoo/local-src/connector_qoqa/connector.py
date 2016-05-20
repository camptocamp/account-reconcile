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

import pytz
from datetime import datetime
from dateutil import parser
from collections import namedtuple
from itertools import tee, izip

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.connector import (install_in_connector,
                                                Environment)
from openerp.addons.connector.checkpoint import checkpoint
from openerp.addons.connector import queue

install_in_connector()

QOQA_TZ = pytz.timezone('Europe/Zurich')


queue.job.RETRY_INTERVAL = 60  # seconds


def iso8601_to_utc_datetime(isodate):
    """ Returns the UTC datetime from an iso8601 date

    A QoQa date is formatted using the ISO 8601 format.
    Example: 2013-11-04T13:52:01+0100
    """
    parsed = parser.parse(isodate)
    if not parsed.tzinfo:
        return parsed
    utc = pytz.timezone('UTC')
    # set as UTC and then remove the tzinfo so the date becomes naive
    return parsed.astimezone(utc).replace(tzinfo=None)


def utc_datetime_to_iso8601(dt):
    """ Returns an iso8601 datetime from a datetime.

    Example: 2013-11-04 12:52:01 → 2013-11-04T12:52:01+0000

    """
    utc = pytz.timezone('UTC')
    utc_dt = utc.localize(dt, is_dst=False)  # UTC = no DST
    return utc_dt.isoformat()


def iso8601_to_local_date(isodate):
    """ Returns the local date from an iso8601 date

    Keep only the date, when we want to keep only the local date.
    It's safe to extract it directly from the tz-aware timestamp.
    Example with 2014-10-07T00:34:59+0200: we want 2014-10-07 and not
    2014-10-06 that we would have using the timestamp converted to UTC.
    """
    local_date = isodate[:10]
    return datetime.strptime(local_date, '%Y-%m-%d').date()


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.browse('qoqa.backend', backend_id)
    env = Environment(backend_record, session, model_name)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    env.set_lang(code=lang_code)
    return env


HistoricInfo = namedtuple('HistoricInfo',
                          ['historic',  # historic data, bypass workflows, ...
                           'active',  # records imported inactive
                           ])


def historic_import(connector_unit, record):
    order_date = iso8601_to_utc_datetime(record['created_at'])
    until_str = connector_unit.backend_record.date_really_import
    inactive_until_str = connector_unit.backend_record.date_import_inactive
    historic_until = datetime.strptime(until_str,
                                       DEFAULT_SERVER_DATETIME_FORMAT)
    inactive_until = datetime.strptime(inactive_until_str,
                                       DEFAULT_SERVER_DATETIME_FORMAT)
    info = HistoricInfo(historic=order_date < historic_until,
                        active=order_date >= inactive_until)
    return info


class qoqa_binding(orm.AbstractModel):
    """ Abstract Model for the Bindings.

    All the models used as bindings between QoQa and OpenERP
    (``qoqa.product.product``, ...) should ``_inherit`` it.
    """
    _name = 'qoqa.binding'
    _inherit = 'external.binding'
    _description = 'QoQa Binding (abstract)'

    _columns = {
        # 'openerp_id': openerp-side id must be declared in concrete model
        'backend_id': fields.many2one(
            'qoqa.backend',
            'QoQa Backend',
            required=True,
            readonly=True,
            ondelete='restrict'),
        'qoqa_id': fields.char('ID on QoQa', select=True),
    }

    def _get_default_backend_id(self, cr, uid, context=None):
        data_obj = self.pool.get('ir.model.data')
        try:
            xmlid = ('connector_qoqa', 'qoqa_backend_config')
            __, backend_id = data_obj.get_object_reference(cr, uid, *xmlid)
        except ValueError:
            return False
        return backend_id

    _defaults = {
        'backend_id': _get_default_backend_id,
    }

    # the _sql_contraints cannot be there due to this bug:
    # https://bugs.launchpad.net/openobject-server/+bug/1151703


def add_checkpoint(session, model_name, record_id, backend_id):
    """ Add a row in the model ``connector.checkpoint`` for a record,
    meaning it has to be reviewed by a user.

    :param session: current session
    :type session: :py:class:`openerp.addons.connector\
                              .session.ConnectorSession`
    :param model_name: name of the model of the record to be reviewed
    :type model_name: str
    :param record_id: ID of the record to be reviewed
    :type record_id: int
    :param backend_id: ID of the Magento Backend
    :type backend_id: int
    """
    return checkpoint.add_checkpoint(session, model_name, record_id,
                                     'qoqa.backend', backend_id)


# sliding window from:
# http://docs.python.org/2/library/itertools.html#recipes
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)
