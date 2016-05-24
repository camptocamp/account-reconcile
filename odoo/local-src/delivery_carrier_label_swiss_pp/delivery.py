# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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


class DeliveryCarrier(orm.Model):
    """ Add service group """
    _inherit = 'delivery.carrier'

    def _get_carrier_type_selection(self, cr, uid, context=None):
        """ Add postlogistics carrier type """
        res = super(DeliveryCarrier, self
                    )._get_carrier_type_selection(cr, uid, context=context)
        res.append(('swiss_apost', 'Swiss A Priority'))
        return res

    _columns = {
        'type': fields.selection(
            _get_carrier_type_selection, 'Type',
            help="Carrier type (combines several delivery methods)"),
    }
