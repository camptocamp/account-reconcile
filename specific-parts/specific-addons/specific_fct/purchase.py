# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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
from openerp.osv import orm


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    # Use the module "purchase_group_hooks" in order to
    # redefine one part from purchase order merge: the notes
    # should not be concatenated.

    def _update_merged_order_data(self, merged_data, order):
        if order.date_order < merged_data['date_order']:
            merged_data['date_order'] = order.date_order
        if order.origin:
            if (
                order.origin not in merged_data['origin']
                and merged_data['origin'] not in order.origin
            ):
                merged_data['origin'] = (
                    (merged_data['origin'] or '') + ' ' + order.origin
                )
        return merged_data
