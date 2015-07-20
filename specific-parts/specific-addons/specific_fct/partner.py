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
        # Since the address is now displayed in the name, it's important
        # to truncate any name value in order to only use the "base" one.
        # In order to do this, we truncate at the first comma.
        if name:
            name = name.split(',')[0]

        # Re-define name_search in order to put QoQa users first
        res = []
        user_args = args + [['user_ids', '!=', False]]
        users = super(res_partner, self).name_search(cr, uid, name, user_args,
                                                     operator, context, limit)
        res = [(id, 'QoQa - ' + username) for (id, username) in users]

        new_limit = None
        if limit is not None:
            if limit > len(users):
                new_limit = limit - len(users)
            else:
                new_limit = 0

        non_user_args = args + [['user_ids', '=', False]]
        res += super(res_partner, self).name_search(
            cr, uid, name, non_user_args, operator, context, new_limit)
        return res

    def name_get(self, cr, uid, ids, context=None):
        """ Custom name get which shows the address next to the name """
        if context is None:
            context = {}
        else:
            context = context.copy()
        if isinstance(ids, (int, long)):
            ids = [ids]
        context['show_address'] = True
        names = super(res_partner, self).name_get(cr, uid, ids,
                                                  context=context)
        res = []
        for partner_id, name in names:
            res.append((partner_id, name.replace('\n', ', ')))
        return res
