# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class QoQaShop(models.Model):
    _inherit = 'qoqa.shop'

    swiss_pp_logo = fields.Binary('Shop logo for PP labels')
