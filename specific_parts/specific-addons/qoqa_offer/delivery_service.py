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


class delivery_service(orm.Model):
    """ A delivery service is sort of type of delivery.

    Examples:

        * A-Mail B5 0-100g 0-2cm
        * Standard w/phone
        * So Colissimo
    """
    _name = 'delivery.service'
    _description = 'Delivery Service'
    _order_by = 'name asc'
    _columns = {
        'name': fields.char('Name'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }
