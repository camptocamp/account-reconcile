# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
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

from openerp.osv import orm, fields


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _order = 'sequence asc, name asc'

    _columns = {
        'sequence': fields.integer(
            string='Sequence'),
    }


# class purchase_order(orm.Model):
#     _inherit = 'purchase.order'
# 
#     _columns = {
#     'partner_ref': fields.char('Supplier Reference',
#                                states={'done':[('readonly',True)]}, size=64,
#                                help="""
#                                Reference of the sales order or quotation sent 
#                                by your supplier. It's mainly used to do the 
#                                matching when you receive the products as this
#                                reference is usually written on the delivery 
#                                order sent by your supplier."""
#                                ),
#     }
