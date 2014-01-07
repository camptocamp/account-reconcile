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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_offer(orm.Model):
    _inherit = 'qoqa.offer'

    _columns = {
        'backend_id': fields.related(
            'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa', select=True),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }

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
