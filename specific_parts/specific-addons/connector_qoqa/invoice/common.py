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

"""
Add an ``active`` field on the invoice so we can import historic
invoice as inactive.

The creation of the imported invoices is handled by
``sale/importer.py``.

Add a link between the refunds and the invoices that generated it.

"""

from requests.exceptions import HTTPError, RequestException, ConnectionError
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import NetworkRetryableError
from .exporter import create_refund
from ..exception import (QoQaResponseNotParsable,
                         QoQaAPISecurityError,
                         QoQaResponseError,
                         )


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'active': fields.boolean('Active'),
        'refund_from_invoice_id': fields.many2one(
            'account.invoice',
            string='Refund generated from invoice',
            ondelete='restrict'),
    }

    _defaults = {
        'active': True,
    }

    def _prepare_refund(self, cr, uid, invoice, date=None, period_id=None,
                        description=None, journal_id=None, context=None):
        result = super(account_invoice, self)._prepare_refund(
            cr, uid, invoice, date=date, period_id=period_id,
            description=description, journal_id=journal_id, context=context)
        result['refund_from_invoice_id'] = invoice.id
        return result

    def refund_on_qoqa(self, cr, uid, ids, context=None):
        """ Create (synchronously) a refund in the qoqa backend.

        If the origin invoice/sales order does not comes from qoqa,
        just return.

        The call is synchronous, if it fails, the refund cannot be
        validated.  The qoqa backend will create a payment using a
        payment service (datatrans) and return a transaction ID.

        """
        for refund in self.browse(cr, uid, ids, context=context):
            invoice = refund.refund_from_invoice_id
            if not invoice:
                continue
            sales = invoice.sale_order_ids
            if not sales or not sales[0].qoqa_bind_ids:
                continue
            qsale = sales[0].qoqa_bind_ids[0]
            session = ConnectorSession(cr, uid, context=context)
            # with .delay() it would be created in a job,
            # here it is called synchronously
            try:
                create_refund(session,
                              'account.invoice',
                              qsale.backend_id.id,
                              refund.id)
            except NetworkRetryableError as err:
                raise orm.except_orm(
                    _('Network Error'),
                    _('Impossible to refund on the backend.\n\n%s') % err)
            except (HTTPError, RequestException, ConnectionError) as err:
                raise orm.except_orm(
                    _('API / Network Error'),
                    _('Impossible to refund on the backend.\n\n%s') % err)
            except QoQaAPISecurityError as err:
                raise orm.except_orm(
                    _('Authentication Error'),
                    _('Impossible to refund on the backend.\n\n%s') % err)
            except QoQaResponseError as err:
                raise orm.except_orm(
                    _('Error(s) on the QoQa Backend'),
                    unicode(err))
            except QoQaResponseNotParsable as err:
                # The response from the backend cannot be parsed, not a
                # JSON.  So we don't know what the error is.
                raise orm.except_orm(
                    _('Unknown Error'),
                    _('The backend failed to create the refund.'))
        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).invoice_validate(
            cr, uid, ids, context=context)
        self.refund_on_qoqa(cr, uid, ids, context=context)
        return result
