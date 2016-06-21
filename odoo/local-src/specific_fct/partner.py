# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


def strip(value):
    if value:
        return value.strip()
    else:
        return ''


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _display_address(self, partner, without_company=False):
        """ Specific code to fix OpenERP behavior: in the view (and the export)
        every text field is stripped of its spaces, so importing an exported
        partner name will fail on the equality check.
        """
        address_format = (
            partner.country_id and partner.country_id.address_format or
            "%(street)s\n%(street2)s\n%(city)s "
            "%(state_code)s %(zip)s\n%(country_name)s"
        )

        args = {
            'state_code': strip(partner.state_id.code),
            'state_name': strip(partner.state_id.name),
            'country_code': strip(partner.country_id.code),
            'country_name': strip(partner.country_id.name),
            'company_name': partner.parent_id and strip(partner.parent_name),
            'street': strip(partner.street),
            'street2': strip(partner.street2),
            'city': strip(partner.city),
            'zip': strip(partner.zip),
            'state_id': partner.state_id or '',
            'country_id': partner.country_id or '',
        }
        if without_company:
            args['company_name'] = ''
        elif partner.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    # TODO:
    # def name_search(self, cr, uid, name, args=None, operator='ilike',
    #                 context=None, limit=100):
    #     # Since the address is now displayed in the name, it's important
    #     # to truncate any name value in order to only use the "base" one.
    #     # In order to do this, we truncate at the first comma.
    #     if name and operator != '=':
    #         name = name.split(',')[0]
    #     if args is None:
    #         args = []
    #
    #     res = []
    #
    #     # limit if unlimited (otherwise, the 2 name_search lead to MemoryError)
    #     if limit is None or limit < 1:
    #         limit = 100
    #
    #     # Re-define name_search in order to put QoQa users first
    #     user_args = args + [['user_ids', '!=', False]]
    #     users = super(ResPartner, self).name_search(cr, uid, name, user_args,
    #                                                  operator, context, limit)
    #     res = [(id, 'QoQa - ' + username) for (id, username) in users]
    #
    #     # search for remaining users (but if limit is 0 or less, avoid search)
    #     new_limit = max(limit - len(users), 0)
    #     if new_limit > 0:
    #         non_user_args = args + [['user_ids', '=', False]]
    #         res += super(ResPartner, self).name_search(
    #             cr, uid, name, non_user_args, operator, context, new_limit)
    #
    #     return res

    # TODO:
    # def name_get(self, cr, uid, ids, context=None):
    #     """ Custom name get which shows the address next to the name """
    #     if context is None:
    #         context = {}
    #     else:
    #         context = context.copy()
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     context['show_address'] = True
    #     names = super(ResPartner, self).name_get(cr, uid, ids,
    #                                               context=context)
    #     res = []
    #     for partner_id, name in names:
    #         res.append((partner_id, name.replace('\n', ', ')))
    #     return res

    # TODO:
    # def init(self, cr):
    #     def create_gin_trgm_index(field):
    #         index_name = 'res_partner_%s_trgm_index' % field
    #         cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
    #                    (index_name,))
    #         if not cr.fetchone():
    #             cr.execute('CREATE INDEX %s '
    #                        'ON res_partner '
    #                        'USING gin (%s gin_trgm_ops)' % (index_name, field))
    #     for field in ('email', 'display_name'):
    #         create_gin_trgm_index(field)
