# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class QoqaShop(models.Model):
    _name = 'qoqa.shop'
    _description = 'QoQa Shop'

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
    )

    kanban_image = fields.Binary(
        'Kanban Image',
        help="Image displayed on the Kanban views for this shop")
