# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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


class crm_claim(orm.Model):
    """ Crm claim
    """
    _inherit = "crm.claim"

    _columns = {
        'company_id': fields.related(
            'warehouse_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            store=True,
            readonly=True
        ),
        'invoice_id': fields.many2one(
            'account.invoice',
            string='Invoice',
            domain=['|', ('active', '=', False), ('active', '=', True)],
            help='Related original Customer invoice'
        ),
        'datatrans_url': fields.char('Datatrans URL', size=256),
    }
