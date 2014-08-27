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


class qoqa_buyphrase(orm.Model):
    _name = 'qoqa.buyphrase'
    _description = 'QoQa Buyphrase'

    _columns = {
        'name': fields.char('Phrase',
                            required=True,
                            translate=True),
        'description': fields.html('Description', translate=True),
        'active': fields.boolean('Active'),
        'qoqa_shop_id': fields.many2one(
            'qoqa.shop',
            string='Shop',
            required=True),
        'action': fields.integer('Action'),
    }

    _defaults = {
        'active': True,
        'action': 1,
    }
