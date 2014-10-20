# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Tristan Rouiller
#    Copyright 2014 QoQa SA
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
from openerp import tools
from openerp import SUPERUSER_ID


class res_users(orm.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    _columns = {
        'qoqa_shop_ids': fields.many2many(
            'qoqa.shop',
            string='Favorites Shops'),
    }

    @tools.ormcache(skiparg=2)
    def context_get(self, cr, uid, context=None):
        result = super(res_users, self).context_get(cr, uid, context)
        user = self.browse(cr, SUPERUSER_ID, uid, context)
        if user.qoqa_shop_ids:
            result['qoqa_shop_ids'] = [shop.id for shop in user.qoqa_shop_ids]
        else:
            qoqa_obj = self.pool['qoqa.shop']
            result['qoqa_shop_ids'] = qoqa_obj.search(cr, uid, [],
                                                      context=context)
        
        return result