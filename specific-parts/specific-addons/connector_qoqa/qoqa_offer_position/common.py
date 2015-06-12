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

from datetime import datetime
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from ..backend import qoqa
from ..unit.backend_adapter import QoQaAdapter
from ..unit.binder import QoQaBinder
from ..unit.backend_adapter import api_handle_errors


class qoqa_offer_position(orm.Model):
    _inherit = 'qoqa.offer.position'

    _columns = {
        'backend_id': fields.related(
            'offer_id', 'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa', select=True),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(qoqa_id)',
         "An offer position with the same ID on QoQa already exists"),
    ]

    def _get_stock_values(self, cr, uid, ids, context=None):
        """Get stock values.

        The original method computes "offline values", that means
        the values computed using the OpenERP stock and sales.

        This inherit of the method adds the "online values" logic: when
        an offer is in progress, the stock values are read from the QoQa
        API so they are realtime and thus more accurate.

        When the QoQa API can't be accessed, it fallbacks to the
        offline values.

        :returns: computed values
        :rtype: dict
        """
        values = super(qoqa_offer_position, self)._get_stock_values(
            cr, uid, ids, context=context)
        session = ConnectorSession(cr, uid, context=context)
        for position in self.browse(cr, uid, ids, context=context):
            # check bounds
            fmt = DEFAULT_SERVER_DATETIME_FORMAT
            # 'begin' and 'end' are in UTC
            begin = datetime.strptime(position.offer_id.datetime_begin_filter,
                                      fmt)
            end = datetime.strptime(position.offer_id.datetime_end_filter, fmt)
            if not (begin <= datetime.now() <= end):
                continue
            env = get_environment(session, self._name,
                                  position.backend_id.id)
            adapter = env.get_connector_unit(OfferPositionAdapter)
            binder = env.get_connector_unit(QoQaBinder)
            qoqa_id = binder.to_backend(position.id)
            if not qoqa_id:
                # so the user knows that it 'should' be displayed
                # but can't actually
                values[position.id]['stock_online_failure'] = True
                values[position.id]['stock_online_failure_message'] = (
                    _('Stock is offline because the offer does not exist '
                      'in the QoQa backend.')
                )
                continue
            try:
                with api_handle_errors(''):
                    qoqa_values = adapter.stock_values(qoqa_id)
            except orm.except_orm as error:
                # api_handle_errors will return an orm.except_orm
                # if a network or api error occurs
                if error.value:
                    message = "%s: %s" % (error.name, error.value.strip('\n'))
                else:
                    message = error.name  # on 'Unknow Error'
                computed = {
                    'stock_is_online': False,
                    'stock_online_failure': True,
                    'stock_online_failure_message': message,
                }
            else:
                if 'sold' in qoqa_values and qoqa_values['sold']:
                    sold = int(qoqa_values['sold'])
                    quantity = values[position.id]['sum_quantity']
                    residual = quantity - sold
                    progress = 0.0
                    if quantity > 0:
                        progress = ((quantity - residual) / quantity) * 100

                    reserved = int(qoqa_values['reserved'])
                    reserved_percent = 0.0
                    if quantity > 0:
                        progress = reserved / quantity * 100

                    computed = {
                        'stock_is_online': True,
                        'stock_online_failure': False,
                        'stock_online_failure_message': '',
                        'sum_stock_sold': sold,
                        'sum_residual': residual,
                        'stock_progress': progress,
                        'stock_progress_remaining': 100 - progress,
                        'stock_reserved': reserved,
                        'stock_reserved_percent': reserved_percent,
                    }
                else:
                    computed = {
                        'stock_is_online': False,
                        'stock_online_failure': True,
                        'stock_online_failure_message': _('API did not return'
                                                          'the stock values.'),
                    }
            values[position.id].update(computed)

        return values

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
                  'using the "active" checkbox.'))
        return super(qoqa_offer_position, self).unlink(cr, uid, ids,
                                                       context=context)


@qoqa
class OfferPositionAdapter(QoQaAdapter):
    _model_name = 'qoqa.offer.position'
    _endpoint = 'offer'

    def stock_values(self, id):
        """ Read the sold and reserved stock values on QoQa """
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        payload = {'action': 'get_stock'}
        response = self.client.get(url + str(id),
                                   params=payload,
                                   headers=headers)
        response = self._handle_response(response)
        return response['data']


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
