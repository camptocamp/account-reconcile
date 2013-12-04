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
from ..backend import qoqa
from ..unit.backend_adapter import QoQaAdapter
from ..unit.binder import QoQaBinder


class qoqa_offer_position(orm.Model):
    _inherit = 'qoqa.offer.position'

    _columns = {
        'backend_id': fields.related(
            'offer_id', 'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa'),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
            'qoqa_sync_date': False,
        })
        return super(qoqa_offer_position, self).copy_data(
            cr, uid, id, default=default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        positions = self.browse(cr, uid, ids, context=context)
        if any(pos for pos in positions if pos.qoqa_id):
            raise orm.except_orm(
                _('Error'),
                _('Exported positions can not be deleted when '
                  'they have been exported. They can still be deactivated '
                  'using the "active" box.'))
        return super(qoqa_offer_position, self).unlink(cr, uid, ids, context=context)


@qoqa
class OfferPositionAdapter(QoQaAdapter):
    _model_name = 'qoqa.offer.position'
    _endpoint = 'offer'


@qoqa
class RegularPriceTypeBinder(QoQaBinder):
    """ 'Fake' binder: hard code bindings

    ``regular_price_type`` is a selection field on
    `qoqa.offer.position``.

    The binding is a mapping between the name of the
    selection on OpenERP and the id on QoQa.

    """
    _model_name = 'qoqa.regular.price.type'

    qoqa_bindings = {1: 'normal', 2: 'no_price', 3: 'direct'}
    # inverse mapping
    openerp_bindings = dict((v, k) for k, v in qoqa_bindings.iteritems())

    def to_openerp(self, external_id, unwrap=False):
        return self.qoqa_bindings[external_id]

    def to_backend(self, binding_id, wrap=False):
        return self.openerp_bindings[binding_id]

    def bind(self, external_id, binding_id):
        raise TypeError('%s cannot be synchronized' % self._model_name)
