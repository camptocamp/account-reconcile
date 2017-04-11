# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import api, fields, models, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    display_name = fields.Char(compute='_compute_display_name',
                               string='Name')

    @api.multi
    @api.depends('parent_id', 'is_company', 'name',
                 'street', 'street2', 'zip', 'city',
                 'state_id', 'country_id')
    def _compute_display_name(self):
        for partner in self:
            partner.display_name = partner.name_get()[0][1]

    @api.model
    def _display_address(self, address, without_company=False):
        """ Specific code to fix OpenERP behavior: in the view (and the export)
        every text field is stripped of its spaces, so importing an exported
        partner name will fail on the equality check.
        """
        # for QoQa customers, the company name is their login/email,
        # so we don't want to show it in the address
        if address.qoqa_bind_ids or address.parent_id.qoqa_bind_ids:
            without_company = True
        address = super(ResPartner, self)._display_address(
            address,
            without_company=without_company
        )
        address = '\n'.join(l.strip() for l in address.split('\n'))
        return address

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
        if self.env.context.get('_name_get_report'):
            res = []
            for partner in self:
                if partner.qoqa_bind_ids or partner.parent_id.qoqa_bind_ids:
                    name = partner.name
                    name = name + "\n" + self._display_address(
                        partner,
                        without_company=True
                    )
                    name = name.replace('\n\n', '\n')
                    name = name.replace('\n\n', '\n')
                    res.append((partner.id, name))
                else:
                    res += super(ResPartner, partner).name_get()
            return res
        names = \
            super(ResPartner, self.with_context(show_address=True)).name_get()
        res = []
        for partner_id, name in names:
            parts = (p.strip() for p in name.splitlines() if p.strip())
            res.append((partner_id, ', '.join(parts)))
        return res

    @api.model
    def _trgm_extension_exists(self):
        self.env.cr.execute("""
            SELECT name, installed_version
            FROM pg_available_extensions
            WHERE name = 'pg_trgm'
            LIMIT 1;
            """)

        extension = self.env.cr.fetchone()
        if extension is None:
            return 'missing'

        if extension[1] is None:
            return 'uninstalled'

        return 'installed'

    @api.model
    def _is_postgres_superuser(self):
        self.env.cr.execute("SHOW is_superuser;")
        superuser = self.env.cr.fetchone()
        return superuser is not None and superuser[0] == 'on' or False

    @api.model
    def _install_trgm_extension(self):
        extension = self._trgm_extension_exists()
        if extension == 'missing':
            _logger.warning('To use pg_trgm you have to install the '
                            'postgres-contrib module.')
        elif extension == 'uninstalled':
            if self._is_postgres_superuser():
                self.env.cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                return True
            else:
                _logger.warning('To use pg_trgm you have to create the '
                                'extension pg_trgm in your database or you '
                                'have to be the superuser.')
        else:
            return True
        return False

    def init(self, cr):
        installed = self._install_trgm_extension(cr, SUPERUSER_ID, context={})
        cr.commit()

        def create_gin_trgm_index(field):
            index_name = 'res_partner_%s_trgm_index' % field
            cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                       (index_name,))
            if not cr.fetchone():
                cr.execute('CREATE INDEX %s '
                           'ON res_partner '
                           'USING gin (%s gin_trgm_ops)' % (index_name, field))
        if installed:
            for field in ('email', 'display_name', 'ref'):
                create_gin_trgm_index(field)
