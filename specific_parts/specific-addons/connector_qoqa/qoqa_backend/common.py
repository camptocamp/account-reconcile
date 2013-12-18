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

import requests

from datetime import datetime
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.session import ConnectorSession
from ..unit.backend_adapter import QoQaAdapter
from ..unit.import_synchronizer import (import_batch,
                                        import_batch_divider,
                                        import_record,
                                        )
from ..connector import get_environment
from ..exception import QoQaAPISecurityError, QoQaResponseNotParsable

"""
We'll have 1 ``qoqa.backend`` sharing the connection informations probably,
linked to several ``qoqa.shop``.

"""


class qoqa_backend(orm.Model):
    _name = 'qoqa.backend'
    _description = 'QoQa Backend'
    _inherit = 'connector.backend'
    _backend_type = 'qoqa'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('v1', 'v1'),
                ]

    _columns = {
        # override because the version has no meaning here
        'version': fields.selection(
            _select_versions,
            string='API Version',
            required=True),
        'default_lang_id': fields.many2one(
            'res.lang',
            'Default Language',
            required=True,
            help="If a default language is selected, the records "
                 "will be imported in the translation of this language.\n"
                 "Note that a similar configuration exists for each shop."),
        'url': fields.char('URL', required=True),
        'client_key': fields.char('Client Key'),
        'client_secret': fields.char('Client Secret'),
        'access_token': fields.char('OAuth Token'),
        'access_token_secret': fields.char('OAuth Token Secret'),
        'debug': fields.boolean('Debug'),

        'property_voucher_journal_id': fields.property(
            'account.journal',
            type='many2one',
            relation='account.journal',
            view_load=True,
            string='Journal for Vouchers',
            domain="[('type', '=', 'bank')]"),

        'import_product_template_from_date': fields.datetime(
            'Import product templates from date', required=True),
        'import_product_product_from_date': fields.datetime(
            'Import product variants from date', required=True),
        'import_res_partner_from_date': fields.datetime(
            'Import Customers from date', required=True),
        'import_address_from_date': fields.datetime(
            'Import Addresses from date', required=True),
        'import_sale_order_from_date': fields.datetime(
            'Import Sales Orders from date', required=True),
        'import_promo_issuance_from_date': fields.datetime(
            'Import Promo Issuances from date', required=True),
        'import_sale_id': fields.char('Sales Order ID'),
        'import_variant_id': fields.char('Variant ID'),
        'import_offer_id': fields.char('Offer ID'),
        'import_offer_position_id': fields.char('Offer Position ID'),
        'import_promo_issuance_id': fields.char('Promo Issuance ID'),

        'date_really_import': fields.datetime(
            'Import historic only until', required=True,
            help="Before this date, the sales order will be imported "
                 "without accounting entries."),
        'date_import_inactive': fields.datetime(
            'Sales Orders Inactive before', required=True,
            help="Before this date, the sales order will be imported "
                 "as inactive"),
    }

    _defaults = {
        # earlier dates for the imports, nothing existed before
        # we need a start date in order to import them by week
        'import_product_template_from_date': '2005-12-12 00:00:00',
        'import_product_product_from_date': '2005-12-12 00:00:00',
        'import_res_partner_from_date': '2005-12-12 00:00:00',
        'import_address_from_date': '2005-12-12 00:00:00',
        'import_sale_order_from_date': '2005-12-12 00:00:00',
        'import_promo_issuance_from_date': '2005-12-12 00:00:00',
        'date_really_import': '2014-01-01 00:00:00',
        'date_import_inactive': '2012-01-01 00:00:00',
    }

    def check_connection(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "Only 1 ID accepted, got %r" % ids
            ids = ids[0]
        session = ConnectorSession(cr, uid, context=context)
        env = get_environment(session, 'qoqa.shop', ids)
        adapter = env.get_connector_unit(QoQaAdapter)
        try:
            adapter.search()
        except QoQaAPISecurityError as err:
            raise orm.except_orm(_('Security Error'), err)
        except QoQaResponseNotParsable:
            # when the OAuth is not valid, QoQa redirect to the login
            # page, thus, we get an unparseable HTML login page
            raise orm.except_orm(
                _('Authentification Error'),
                _('The authentification failed. Use the '
                  '"Get Authentication Tokens" button to request access'))
        except requests.exceptions.HTTPError as err:
            raise orm.except_orm(_('Error'), err)
        raise orm.except_orm('Ok', 'Connection is successful.')

    def synchronize_metadata(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
        for backend_id in ids:
            # import directly, do not delay because this
            # is a fast operation, a direct return is fine
            # and it is simpler to import them sequentially
            import_batch(session, 'qoqa.shop', backend_id)
        return True

    def create(self, cr, uid, vals, context=None):
        existing_ids = self.search(cr, uid, [], context=context)
        if existing_ids:
            raise orm.except_orm(
                _('Error'),
                _('Only 1 QoQa configuration is allowed.'))
        return super(qoqa_backend, self).create(cr, uid, vals, context=context)

    def _import_from_date(self, cr, uid, ids, model,
                          from_date_field, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        DT_FMT = DEFAULT_SERVER_DATETIME_FORMAT
        session = ConnectorSession(cr, uid, context=context)
        import_start_time = datetime.now().strftime(DT_FMT)
        for backend in self.browse(cr, uid, ids, context=context):
            from_date = getattr(backend, from_date_field)
            if from_date:
                from_date = datetime.strptime(from_date, DT_FMT)
            else:
                from_date = None
            import_batch_divider(session, model, backend.id,
                                 from_date=from_date)
        self.write(cr, uid, ids,
                   {from_date_field: import_start_time})

    def import_product_template(self, cr, uid, ids, context=None):
        self._import_from_date(cr, uid, ids, 'qoqa.product.template',
                               'import_product_template_from_date',
                               context=context)
        return True

    def import_product_product(self, cr, uid, ids, context=None):
        self._import_from_date(cr, uid, ids, 'qoqa.product.product',
                               'import_product_product_from_date',
                               context=context)
        return True

    def import_res_partner(self, cr, uid, ids, context=None):
        self._import_from_date(cr, uid, ids, 'qoqa.res.partner',
                               'import_res_partner_from_date',
                               context=context)
        return True

    def import_address(self, cr, uid, ids, context=None):
        self._import_from_date(cr, uid, ids, 'qoqa.address',
                               'import_address_from_date',
                               context=context)
        return True

    def import_sale_order(self, cr, uid, ids, context=None):
        self._import_from_date(cr, uid, ids, 'qoqa.sale.order',
                               'import_sale_order_from_date',
                               context=context)
        return True

    def import_promo_issuance(self, cr, uid, ids, context=None):
        self._import_from_date(cr, uid, ids, 'qoqa.promo.issuance.line',
                               'import_promo_issuance_from_date',
                               context=context)
        return True

    def _import_one(self, cr, uid, ids, model, field, context=None):
        session = ConnectorSession(cr, uid, context=context)
        for backend in self.browse(cr, uid, ids, context=context):
            record_id = backend[field]
            if not record_id:
                continue
            import_record(session, model, backend.id,
                          record_id, force=True)

    def import_one_sale_order(self, cr, uid, ids, context=None):
        self._import_one(cr, uid, ids, 'qoqa.sale.order',
                         'import_sale_id', context=context)
        return True

    def import_one_variant(self, cr, uid, ids, context=None):
        self._import_one(cr, uid, ids, 'qoqa.product.product',
                         'import_variant_id', context=context)
        return True

    def import_one_offer_position(self, cr, uid, ids, context=None):
        self._import_one(cr, uid, ids, 'qoqa.offer.position',
                         'import_offer_position_id', context=context)
        return True

    def import_one_promo_issuance(self, cr, uid, ids, context=None):
        self._import_one(cr, uid, ids, 'qoqa.promo.issuance.line',
                         'import_promo_issuance_id', context=context)
        return True

    def import_one_offer(self, cr, uid, ids, context=None):
        self._import_one(cr, uid, ids, 'qoqa.offer',
                         'import_offer_id', context=context)
        return True

    def _exec_scheduler_callback(self, cr, uid, callback, context=None):
        ids = self.search(cr, uid, [], context=context)
        callback(cr, uid, ids, context=context)

    def _scheduler_import_sale_order(self, cr, uid, context=None):
        self._exec_scheduler_callback(cr, uid, self.import_sale_order,
                                      context=context)

    def _scheduler_import_res_partner(self, cr, uid, context=None):
        self._exec_scheduler_callback(cr, uid, self.import_res_partner,
                                      context=context)

    def _scheduler_import_address(self, cr, uid, context=None):
        self._exec_scheduler_callback(cr, uid, self.import_address,
                                      context=context)

    def _scheduler_promo_issuance(self, cr, uid, context=None):
        self._exec_scheduler_callback(cr, uid, self.import_promo_issuance,
                                      context=context)
