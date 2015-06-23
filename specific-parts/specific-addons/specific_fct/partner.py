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
from openerp.osv import orm


class res_partner(orm.Model):
    """ Change default value to comment in order to send people the email
    (for claims)
    """
    _inherit = 'res.partner'

    _defaults = {
        'notification_email_send': 'comment',
    }

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        # Re-define name_search in order to put QoQa users first
        res = []
        user_args = args + [['user_ids', '!=', False]]
        users = super(res_partner, self).name_search(cr, uid, name, user_args,
                                                     operator, context, limit)
        res = [(id, 'QoQa - ' + username) for (id, username) in users]

        if limit > len(users):
            non_user_args = args + [['user_ids', '=', False]]
            new_limit = limit - len(users)
            res += super(res_partner, self).name_search(
                cr, uid, name, non_user_args, operator, context, new_limit)
        return res
