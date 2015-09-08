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


class res_partner(orm.Model):
    """ Change default value to comment in order to send people the email
    (for claims)
    """
    _inherit = 'res.partner'

    def _display_name_compute(self, cr, uid, ids, name, args, context=None):
        return dict(self.name_get(cr, uid, ids, context=context))

    _display_name_store_triggers = {
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.search(cr, uid, [('id', 'child_of', ids)]),
                        ['parent_id', 'is_company',
                         'name', 'firstname', 'lastname',
                         'street', 'street2', 'zip', 'city',
                         'state_id', 'country_id'], 10)
        }

    # indirection to avoid passing a copy of the overridable method
    # when declaring the function field
    _display_name = lambda self, *args, **kwargs: \
        self._display_name_compute(*args, **kwargs)

    _columns = {
        # extra field to allow ORDER BY to match visible names
        'display_name': fields.function(_display_name, type='char',
                                        string='Name',
                                        store=_display_name_store_triggers),
        }

    _defaults = {
        'notification_email_send': 'comment',
    }

    def _display_address(self, cr, uid, address, without_company=False,
                         context=None):
        '''
        Specific code to fix OpenERP behavior: in the view (and the export),
        every text field is stripped of its spaces, so importing an exported
        partner name will fail on the equality check.
        '''
        address_format = (address.country_id and
                          address.country_id.address_format or
                          "%(street)s\n%(street2)s\n%(city)s "
                          "%(state_code)s %(zip)s\n%(country_name)s")
        args = {
            'state_code': address.state_id and
            address.state_id.code and
            address.state_id.code.strip() or '',
            'state_name': address.state_id and
            address.state_id.name and
            address.state_id.name.strip() or '',
            'country_code': address.country_id and
            address.country_id.code and
            address.country_id.code.strip() or '',
            'country_name': address.country_id and
            address.country_id.name and
            address.country_id.name.strip() or '',
            'company_name': address.parent_id and
            address.parent_name and
            address.parent_name.strip() or '',
            'street': address.street and
            address.street.strip() or '',
            'street2': address.street2 and
            address.street2.strip() or '',
            'city': address.city and
            address.city.strip() or '',
            'zip': address.zip and
            address.zip.strip() or '',
            'state_id': address.state_id or '',
            'country_id': address.country_id or '',
        }
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        print args
        return address_format % args

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        # Since the address is now displayed in the name, it's important
        # to truncate any name value in order to only use the "base" one.
        # In order to do this, we truncate at the first comma.
        if name and operator != '=':
            name = name.split(',')[0]
        if args is None:
            args = []

        res = []

        # limit if unlimited (otherwise, the 2 name_search lead to MemoryError)
        if limit is None or limit < 1:
            limit = 100

        # Re-define name_search in order to put QoQa users first
        user_args = args + [['user_ids', '!=', False]]
        users = super(res_partner, self).name_search(cr, uid, name, user_args,
                                                     operator, context, limit)
        res = [(id, 'QoQa - ' + username) for (id, username) in users]

        # search for remaining users (but if limit is 0 or less, avoid search)
        new_limit = max(limit - len(users), 0)
        if new_limit > 0:
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

    def init(self, cr):
        def create_gin_trgm_index(field):
            index_name = 'res_partner_%s_trgm_index' % field
            cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                       (index_name,))
            if not cr.fetchone():
                cr.execute('CREATE INDEX %s '
                           'ON res_partner '
                           'USING gin (%s gin_trgm_ops)' % (index_name, field))
        for field in ('email', 'display_name'):
            create_gin_trgm_index(field)
