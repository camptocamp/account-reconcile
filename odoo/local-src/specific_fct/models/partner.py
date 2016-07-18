# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


def strip(value):
    if value:
        return value.strip()
    else:
        return ''


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('parent_id', 'is_company', 'name', 'firstname',
                 'lastname', 'street', 'street2', 'zip', 'city',
                 'state_id', 'country_id')
    def _display_name_compute(self):
        return self.name_get()

    # indirection to avoid passing a copy of the overridable method
    # when declaring the function field
    def _display_name(self, *args, **kwargs):
        return self._display_name_compute(*args, **kwargs)

    display_name = fields.Char(compute=_display_name,
                               string='Name')

    @api.model
    def _display_address(self, address, without_company=False):
        """ Specific code to fix OpenERP behavior: in the view (and the export)
        every text field is stripped of its spaces, so importing an exported
        partner name will fail on the equality check.
        """
        address_format = (
            address.country_id and address.country_id.address_format or
            "%(street)s\n%(street2)s\n%(city)s "
            "%(state_code)s %(zip)s\n%(country_name)s"
        )

        args = {
            'state_code': strip(address.state_id.code),
            'state_name': strip(address.state_id.name),
            'country_code': strip(address.country_id.code),
            'country_name': strip(address.country_id.name),
            'company_name': strip(address.parent_name),
            'street': strip(address.street),
            'street2': strip(address.street2),
            'city': strip(address.city),
            'zip': strip(address.zip),
            'state_id': address.state_id,
            'country_id': address.country_id
        }
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
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
        users = super(ResPartner, self).name_search(
            name, user_args, operator, limit=limit)
        res = [(id, 'QoQa - ' + username) for (id, username) in users]

        # search for remaining users (but if limit is 0 or less, avoid search)
        new_limit = max(limit - len(users), 0)
        if new_limit > 0:
            non_user_args = args + [['user_ids', '=', False]]
            res += super(ResPartner, self).name_search(
                name, non_user_args, operator, limit=new_limit)

        return res

    @api.multi
    def name_get(self):
        """ Custom name get which shows the address next to the name """
        names = \
            super(ResPartner, self.with_context(show_address=True)).name_get()
        res = []
        for partner_id, name in names:
            res.append((partner_id, name.replace('\n', ', ')))
        return res

    def init(self, cr):
        cr.execute("""
            CREATE EXTENSION IF NOT EXISTS pg_trgm
        """)
        cr.commit()

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
