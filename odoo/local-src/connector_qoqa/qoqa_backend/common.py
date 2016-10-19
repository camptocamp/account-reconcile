# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
We'll have 1 ``qoqa.backend`` sharing the connection informations probably,
linked to several ``qoqa.shop``.

"""

import json
import logging

from datetime import datetime, timedelta

import requests
import psycopg2

from openerp import models, fields, api, exceptions, _

from openerp.addons.connector.session import ConnectorSession
from ..unit.backend_adapter import QoQaAdapter, api_handle_errors
from ..unit.importer import import_batch, import_batch_divider, import_record
from ..backend import qoqa
from ..connector import get_environment
from ..exception import QoQaAPIAuthError

_logger = logging.getLogger(__name__)

IMPORT_DELTA = 10  # seconds


class QoqaBackend(models.Model):
    _name = 'qoqa.backend'
    _description = 'QoQa Backend'
    _inherit = 'connector.backend'
    _backend_type = 'qoqa'

    @api.model
    def _select_versions(self):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('v1', 'v1'),
                ]

    # override because the version has no meaning here
    version = fields.Selection(
        selection=_select_versions,
        string='API Version',
        required=True,
    )
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        required=True,
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.\n"
             "Note that a similar configuration exists for each shop.",
    )
    url = fields.Char(string='URL')
    site_url = fields.Char(string='Site URL')
    token = fields.Char('Token')
    debug = fields.Boolean('Debug')

    property_voucher_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal for Vouchers',
        domain="[('type', '=', 'general')]",
        company_dependent=True,
    )
    promo_type_ids = fields.One2many(
        comodel_name='qoqa.promo.type',
        inverse_name='backend_id',
        string='Promo Types',
    )

    import_res_partner_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_res_partner_from_date',
        string='Import Customers from date',
    )
    import_address_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_address_from_date',
        string='Import Addresses from date',
    )
    import_sale_order_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_sale_order_from_date',
        string='Import Sales Orders from date',
    )
    import_discount_accounting_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_discount_accounting_from_date',
        string='Import Discount Accounting from date',
    )
    import_offer_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_offer_from_date',
        string='Import Offer (descriptions) from date',
    )
    import_product_template_image_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_product_template_image_from_date',
        string='Import Product Images from date',
    )
    import_crm_claim_from_date = fields.Datetime(
        compute='_compute_last_import_date',
        inverse='_inverse_import_crm_claim_from_date',
        string='Import Claims from date',
    )

    import_sale_id = fields.Char(string='Sales Order ID')
    import_variant_id = fields.Char(string='Variant ID')
    import_offer_id = fields.Char(string='Offer ID')
    import_discount_accounting_id = fields.Char(
        string='Discount Accounting Group ID'
    )
    import_address_id = fields.Char(string='Address ID')

    @api.multi
    @api.depends()
    def _compute_last_import_date(self):
        for backend in self:
            self.env.cr.execute("""
                SELECT from_date_field, import_start_time
                FROM qoqa_backend_timestamp
                WHERE backend_id = %s""", (backend.id,))
            rows = self.env.cr.dictfetchall()
            for row in rows:
                field = row['from_date_field']
                timestamp = row['import_start_time']
                if field in self._fields:
                    backend[field] = timestamp

    @api.multi
    def _inverse_date_fields(self, field_name):
        for rec in self:
            timestamp_id = self._lock_timestamp(field_name)
            self._update_timestamp(timestamp_id, field_name,
                                   getattr(rec, field_name))

    @api.multi
    def _inverse_import_res_partner_from_date(self):
        ts_field = 'import_res_partner_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def _inverse_import_address_from_date(self):
        ts_field = 'import_address_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def _inverse_import_sale_order_from_date(self):
        ts_field = 'import_sale_order_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def _inverse_import_discount_accounting_from_date(self):
        ts_field = 'import_discount_accounting_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def _inverse_import_offer_from_date(self):
        ts_field = 'import_offer_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def _inverse_import_product_template_image_from_date(self):
        ts_field = 'import_product_template_image_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def _inverse_import_crm_claim_from_date(self):
        ts_field = 'import_crm_claim_from_date'
        self._inverse_date_fields(ts_field)

    @api.multi
    def check_connection(self):
        self.ensure_one()
        session = ConnectorSession.from_env(self.env)
        with get_environment(session, 'qoqa.shop', self.id) as connector_env:
            adapter = connector_env.get_connector_unit(QoQaAdapter)
            try:
                adapter.search()
            except QoQaAPIAuthError as err:
                raise exceptions.UserError(
                    _('The authentication failed. Use the '
                      '"Get Authentication Tokens" button to request access.'))
            except requests.exceptions.HTTPError as err:
                raise exceptions.UserError(err)
            raise exceptions.UserError('Connection is successful.')

    @api.multi
    def synchronize_metadata(self):
        session = ConnectorSession.from_env(self.env)
        for backend in self:
            # import directly, do not delay because this
            # is a fast operation, a direct return is fine
            # and it is simpler to import them sequentially
            with api_handle_errors():
                import_batch(session, 'qoqa.shop', backend.id)
                import_batch(session, 'qoqa.shipping.fee', backend.id)
        return True

    @api.model
    def get_singleton(self):
        return self.env.ref('connector_qoqa.qoqa_backend_config')

    @api.model
    def create(self, vals):
        existing = self.search([])
        if existing:
            raise exceptions.UserError(
                _('Only 1 QoQa configuration is allowed.')
            )
        return super(QoqaBackend, self).create(vals)

    @api.multi
    def _lock_timestamp(self, from_date_field):
        """ Update the timestamp for a synchro

        thus, we prevent 2 synchros to be launched at the same time.
        The lock is released at the commit of the transaction.

        Return the id of the timestamp if the lock could be acquired.
        """
        assert from_date_field
        self.ensure_one()
        query = """
               SELECT id FROM qoqa_backend_timestamp
               WHERE backend_id=%s
               AND from_date_field=%s
               FOR UPDATE NOWAIT
            """
        try:
            self.env.cr.execute(
                query, (self.id, from_date_field)
            )
        except psycopg2.OperationalError:
            raise exceptions.UserError(
                _("The synchronization timestamp %s is currently locked, "
                  "probably due to an ongoing synchronization." %
                  from_date_field)
            )
        row = self.env.cr.fetchone()
        return row[0] if row else None

    @api.multi
    def _update_timestamp(self, timestamp_id,
                          from_date_field, import_start_time):
        """ Update import timestamp for a synchro

        This method is called to update or create one import timestamp
        for a qoqa.backend. A concurrency error can arise, but it's
        handled in _import_from_date.
        """
        self.ensure_one()
        if not import_start_time:
            return
        if timestamp_id:
            self.env.cr.execute(
                """UPDATE qoqa_backend_timestamp
                   SET import_start_time=%s
                   WHERE id=%s""",
                (import_start_time, timestamp_id)
            )
        else:
            self.env.cr.execute(
                """INSERT INTO qoqa_backend_timestamp
                   (backend_id, from_date_field, import_start_time)
                   VALUES (%s, %s, %s)""",
                (self.id, from_date_field, import_start_time)
            )

    @api.multi
    def _import_from_date(self, model, from_date_field):
        """ Import records from a date

        Create jobs and update the sync timestamp in a savepoint; if a
        concurrency issue arises, it will be logged and rollbacked silently.
        """
        self.ensure_one()
        with self.env.cr.savepoint():
            session = ConnectorSession.from_env(self.env)
            import_start_time = datetime.now()
            try:
                self._lock_timestamp(from_date_field)
            except exceptions.UserError:
                # lock could not be acquired, it is already running and
                # locked by another transaction
                _logger.warning("Failed to update timestamps "
                                "for backend: %s and field: %s",
                                self, from_date_field, exc_info=True)
                return
            from_date = getattr(self, from_date_field)
            if from_date:
                from_date = fields.Datetime.from_string(from_date)
            else:
                from_date = None
            import_batch_divider(session, model, self.id,
                                 from_date=from_date,
                                 to_date=import_start_time,
                                 priority=9)

            # reimport next records a small delta before the last import date
            # in case of small lag between servers or transaction committed
            # after the last import but with a date before the last import
            next_time = import_start_time - timedelta(seconds=IMPORT_DELTA)
            next_time = fields.Datetime.to_string(next_time)
            setattr(self, from_date_field, next_time)

    @api.multi
    def import_res_partner(self):
        self._import_from_date('qoqa.res.partner',
                               'import_res_partner_from_date')
        return True

    @api.multi
    def import_address(self):
        self._import_from_date('qoqa.address', 'import_address_from_date')
        return True

    @api.multi
    def import_sale_order(self):
        self._import_from_date('qoqa.sale.order',
                               'import_sale_order_from_date')
        return True

    @api.multi
    def import_discount_accounting(self):
        self._import_from_date('qoqa.discount.accounting',
                               'import_discount_accounting_from_date')
        return True

    @api.multi
    def import_offer(self):
        self._import_from_date('qoqa.offer', 'import_offer_from_date')
        return True

    @api.multi
    def import_product_template_image(self):
        self._import_from_date('qoqa.offer',
                               'import_product_template_image_from_date')
        return True

    @api.multi
    def import_crm_claim(self):
        self._import_from_date('qoqa.crm.claim', 'import_crm_claim_from_date')
        return True

    @api.multi
    def _import_one(self, model, field, import_func=None):
        if import_func is None:
            import_func = import_record
        session = ConnectorSession.from_env(self.env)
        for backend in self:
            qoqa_record_id = getattr(backend, field)
            if not qoqa_record_id:
                continue
            import_func(session, model, backend.id,
                        qoqa_record_id, force=True)

    @api.multi
    def import_one_sale_order(self):
        self._import_one('qoqa.sale.order', 'import_sale_id')
        return True

    @api.multi
    def import_one_variant(self):
        self._import_one('qoqa.product.product', 'import_variant_id')
        return True

    @api.multi
    def import_one_offer(self):
        self._import_one('qoqa.offer', 'import_offer_id')
        return True

    @api.multi
    def import_one_discount_accounting(self):
        self._import_one('qoqa.discount.accounting',
                         'import_discount_accounting_id')
        return True

    @api.multi
    def import_one_address(self):
        self._import_one('qoqa.address', 'import_address_id')
        return True

    @api.model
    def _scheduler_import_sale_order(self):
        self.import_sale_order(self.search([]))

    @api.model
    def _scheduler_import_res_partner(self):
        self.import_res_partner(self.search([]))

    @api.model
    def _scheduler_import_address(self):
        self.import_address(self.search([]))

    @api.model
    def _scheduler_discount_accounting(self):
        self.import_discount_accounting(self.search([]))

    @api.model
    def _scheduler_import_offer(self):
        self.import_offer(self.search([]))

    @api.model
    def _scheduler_import_product_template_image(self):
        self.import_product_template_image(self.search([]))

    @api.model
    def _scheduler_import_crm_claim(self):
        self.import_crm_claim(self.search([]))


class QoqaBackendTimestamp(models.Model):
    _name = 'qoqa.backend.timestamp'
    _description = 'QoQa Backend Import Timestamps'

    backend_id = fields.Many2one(
        comodel_name='qoqa.backend',
        string='QoQa Backend',
        required=True,
    )
    from_date_field = fields.Char(
        string='From Date Field',
        required=True,
    )
    import_start_time = fields.Datetime(
        string='Import Start Time',
        required=True,
    )


@qoqa
class AuthAdapter(QoQaAdapter):
    _model_name = 'qoqa.backend'
    _endpoint = 'auth'

    def authenticate(self, login, password):
        url = self.url()
        vals = {'user': {'login': login,
                         'password': password},
                'device': {'identifier': 'Odoo'}
                }
        response = self.client.post(url, data=json.dumps(vals))
        result = self._handle_response(response)
        return result.get('data', {}).get('attributes', {}).get('token')
