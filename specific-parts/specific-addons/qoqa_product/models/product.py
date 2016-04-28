# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_wine = fields.Boolean(string='Wine')
    is_liquor = fields.Boolean(string='Liquor')

    # Wine and liquor fields
    winemaker_id = fields.Many2one(
        comodel_name='wine.winemaker',
        string='Winemaker',
        ondelete="restrict",
    )
    appellation = fields.Char()
    millesime = fields.Char()
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
    )
    wine_bottle_id = fields.Many2one(
        comodel_name='wine.bottle',
        string='Volume',
        ondelete="restrict",
    )

    # Wine only fields
    wine_short_name = fields.Char()
    wine_region = fields.Char()
    wine_type_id = fields.Many2one(
        comodel_name='wine.type',
        string='Wine Type',
        ondelete="restrict",
    )
    wine_class_id = fields.Many2one(
        comodel_name='wine.class',
        string='Wine Class',
        domain="[('child_ids', '=', False)]",
        ondelete="restrict",
    )

    # Liquor only fields
    ageing = fields.Float()
    abv = fields.Float(string='Alcohol by volume')
