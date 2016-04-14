# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


# TODO: check but I think buyphrase should be removed
class QoqaBuyphrase(models.Model):
    _name = 'qoqa.buyphrase'
    _description = 'QoQa Buyphrase'

    name = fields.Char(string='Phrase',
                       required=True,
                       translate=True)
    description = fields.Html('Description', translate=True)
    active = fields.Boolean('Active', default=True)
    qoqa_shop_id = fields.Many2one(
        comodel_name='qoqa.shop',
        string='Shop',
        required=True,
    )
    action = fields.Integer('Action', default=1)
