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
from ..backend import qoqa
from ..unit.backend_adapter import QoQaAdapter


class qoqa_shop(orm.Model):
    # model created in 'qoqa_offer'
    # we can't add an _inherit from qoqa.binding
    # so we add manually the _columns
    _inherit = 'qoqa.shop'

    _columns = {
        'backend_id': fields.many2one(
            'qoqa.backend',
            'QoQa Backend',
            required=True,
            readonly=True,
            ondelete='restrict'),
        'qoqa_id': fields.char('ID on QoQa'),
        'sync_date': fields.datetime('Last synchronization date'),
        'lang_id': fields.many2one(
            'res.lang',
            'Default Language',
            help="If a default language is selected, the records "
                 "will be imported in the translation of this language.\n"
                 "Note that a similar configuration exists for each shop."),
    }


class sale_shop(orm.Model):
    _inherit = 'sale.shop'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.shop', 'openerp_id',
            string='QoQa Bindings',
            readonly=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(sale_shop, self).copy_data(cr, uid, id,
                                                default=default,
                                                context=context)


@qoqa
class QoQaShopAdapter(QoQaAdapter):
    _model_name = 'qoqa.shop'
    _endpoint = 'shops'

    def search(self, filters=None):
        url = self.url()
        payload = {}
        response = self.client.get(url, params=payload)
        records = self._handle_response(response)
        return records['data']

    def read(self, id):
        result = super(QoQaShopAdapter, self).read(id)
        # read on shops returns all the shops
        return next((shop for shop in result if str(shop['id']) == str(id)),
                    None)
