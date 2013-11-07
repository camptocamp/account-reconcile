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
from dateutil import parser

from openerp.osv import orm, fields
from openerp.addons.connector.connector import (install_in_connector,
                                                Environment)
from openerp.addons.connector.checkpoint import checkpoint

install_in_connector()

QOQA_TZ = pytz.timezone('Europe/Zurich')


def iso8601_to_utc_datetime(isodate):
    """ Returns the UTC date from an iso8601 date

    A QoQa date is formatted using the ISO 8601 format.
    Example: 2013-11-04T13:52:01+0100
    """
    parsed = parser.parse(isodate)
    if not parsed.tzinfo:
        return parsed
    utc = pytz.timezone('UTC')
    # set as UTC and then remove the tzinfo so the date becomes naive
    return parsed.astimezone(utc).replace(tzinfo=None)


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.browse('qoqa.backend', backend_id)
    env = Environment(backend_record, session, model_name)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    env.set_lang(code=lang_code)
    return env


class qoqa_binding(orm.AbstractModel):
    """ Abstract Model for the Bindigs.

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
        'qoqa_id': fields.char('ID on QoQa'),
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
    :type session: :py:class:`openerp.addons.connector.session.ConnectorSession`
    :param model_name: name of the model of the record to be reviewed
    :type model_name: str
    :param record_id: ID of the record to be reviewed
    :type record_id: int
    :param backend_id: ID of the Magento Backend
    :type backend_id: int
    """
    return checkpoint.add_checkpoint(session, model_name, record_id,
                                     'qoqa.backend', backend_id)
