# -*- coding: utf-8 -*-
# © 2014-2016 QoQa SA
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api
from openerp import tools


class ResUsers(models.Model):
    _inherit = 'res.users'

    qoqa_shop_ids = fields.Many2many(
        'qoqa.shop',
        string='Favorites Shops',
    )

    @tools.ormcache()
    @api.model
    def context_get(self):
        result = super(ResUsers, self).context_get()
        user = self.env.user  # user is in SUPERUSER_ID "sudo"
        if user.qoqa_shop_ids:
            result['qoqa_shop_ids'] = [shop.id for shop in user.qoqa_shop_ids]
        else:
            qoqa_model = self.env['qoqa.shop']
            result['qoqa_shop_ids'] = qoqa_model.search([]).ids
        return result
