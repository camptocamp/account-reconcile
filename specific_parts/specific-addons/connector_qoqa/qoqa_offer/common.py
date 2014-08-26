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

import urllib
import urlparse

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp.addons.connector.session import ConnectorSession

from ..connector import get_environment
from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_offer(orm.Model):
    _inherit = 'qoqa.offer'

    def _get_qoqa_link(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        url_template = "http://www.{shop}/{lang}/offer/view/{qoqa_id}"
        for record in self.browse(cr, uid, ids, context=context):
            if not record.qoqa_id:
                res[record.id] = ''
                continue
            if record.lang_id:
                lang = record.lang_id.code[:2]
            elif context.get('lang'):
                lang = context['lang'][:2]
            else:
                lang = 'fr'
            values = {
                'shop': record.qoqa_shop_id.name.lower(),
                'lang': lang,
                'qoqa_id': record.qoqa_id,
            }
            url = url_template.format(**values)
            params = {'show_banner': False}
            # add the parameters to the url
            url_parts = list(urlparse.urlparse(url))
            url_parts[4] = urllib.urlencode(params)
            url = urlparse.urlunparse(url_parts)
            res[record.id] = url
        return res

    def _get_qoqa_edit_link(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        url_template = "{url}/dot/edit/{qoqa_id}"
        for record in self.browse(cr, uid, ids, context=context):
            if not record.qoqa_id:
                res[record.id] = ''
                continue
            values = {
                'url': record.backend_id.url,
                'qoqa_id': record.qoqa_id,
            }
            url = url_template.format(**values)
            res[record.id] = url
        return res

    _columns = {
        'backend_id': fields.related(
            'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa', select=True),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
        'qoqa_link': fields.function(
            _get_qoqa_link,
            string='Link',
            type='char'),
        'qoqa_edit_link': fields.function(
            _get_qoqa_edit_link,
            string='Edit Offer Content',
            type='char'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(qoqa_id)',
         "An offer with the same ID on QoQa already exists"),
    ]

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
            'qoqa_sync_date': False,
        })
        return super(qoqa_offer, self).copy_data(cr, uid, id,
                                                 default=default,
                                                 context=context)

    def button_edit_offer_content(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "1 ID expected, got %s" % ids
            ids = ids[0]
        offer = self.browse(cr, uid, ids, context=context)
        url = offer.qoqa_edit_link
        if not url:
            raise orm.except_orm(
                _('Error'),
                _('The offer has not been exported to the backend yet.')
            )
        action = {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }
        return action

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        offers = self.browse(cr, uid, ids, context=context)
        exported = [offer for offer in offers if offer.qoqa_id]
        if exported:
            raise orm.except_orm(
                _('Error'),
                _('Exported Offers can no longer be deleted (ref: %s).'
                  'They can still be deactivated using the "active" '
                  'checkbox.') % ','.join(offer.ref for offer in exported))
        return super(qoqa_offer, self).unlink(cr, uid, ids, context=context)


@qoqa
class OfferAdapter(QoQaAdapter):
    _model_name = 'qoqa.offer'
    _endpoint = 'deal'
