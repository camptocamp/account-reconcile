# -*- coding: utf-8 -*-
# Author: Joel Grand-Guillaume
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class CrmClaim(models.Model):
    _inherit = "crm.claim"

    qoqa_shop_id = fields.Many2one('qoqa.shop', 'Shop', index=True)
