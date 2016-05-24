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

from ..unit.backend_adapter import QoQaAdapter
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


@qoqa
class QoQaPromo(QoQaAdapter):
    _model_name = 'qoqa.promo'
    _endpoint = 'promo'


class qoqa_promo_type(orm.Model):
    """ Promo types on QoQa.

    Allow to configure the accounting journals and products for
    the promotions.

    Promos are:

        1 Customer service
        2 Marketing
        3 Affiliation
        4 Staff
        5 Mailing

    On the backend:

        http://admin.test02.qoqa.com/promoType

    """
    _name = 'qoqa.promo.type'
    _inherit = 'qoqa.binding'
    _description = 'QoQa Promo Type'

    _columns = {
        'name': fields.char('Name'),
        'property_journal_id': fields.property(
            'account.journal',
            type='many2one',
            relation='account.journal',
            view_load=True,
            string='Journal',
            domain="[('type', '=', 'general')]"),
        'product_id': fields.many2one(
            'product.product',
            string='Product',
            required=True),
    }


@qoqa
class PromoTypeBinder(QoQaDirectBinder):
    _model_name = 'qoqa.promo.type'

    def bind(self, external_id, binding_id):
        """ Company are not synchronized, raise an error """
        raise TypeError('Promo Types are not synchronized, thus, bind() '
                        'is not applicable')
