# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import pytz
from contextlib import contextmanager
from datetime import datetime
from dateutil import parser
from itertools import tee, izip

from openerp import models, fields, api, exceptions, _
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.checkpoint import checkpoint
from openerp.addons.connector import queue

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


@contextmanager
def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.env['qoqa.backend'].browse(backend_id)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    with session.change_context(lang=lang_code):
        # browse in the new odoo Env
        backend_record = session.env['qoqa.backend'].browse(backend_id)
        conn_env = ConnectorEnvironment(backend_record, session, model_name)
        yield conn_env


class QoqaBinding(models.AbstractModel):
    """ Abstract Model for the Bindings.

    All the models used as bindings between QoQa and OpenERP
    (``qoqa.product.product``, ...) should ``_inherit`` it.
    """
    _name = 'qoqa.binding'
    _inherit = 'external.binding'
    _description = 'QoQa Binding (abstract)'

    # openerp-side id must be declared in concrete model
    # openerp_id = fields.Many2one(...)
    backend_id = fields.Many2one(
        comodel_name='qoqa.backend',
        string='QoQa Backend',
        required=True,
        readonly=True,
        ondelete='restrict',
        default=lambda self: self._default_backend_id(),
    )
    qoqa_id = fields.Char(string='ID on QoQa', index=True)

    @api.model
    def _default_backend_id(self):
        return self.env['qoqa.backend'].get_singleton()

    _sql_constraints = [
        ('qoqa_binding_uniq', 'unique(backend_id, qoqa_id)',
         "A binding already exists for this QoQa record"),
    ]

    @api.multi
    def unlink(self):
        if any(self.mapped('qoqa_id')):
            raise exceptions.UserError(
                _('Exported binding cannot be deleted.')
            )
        return super(QoqaBinding, self).unlink()


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
