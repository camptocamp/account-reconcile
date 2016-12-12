# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # TODO: in connector_qoqa: ensure that when we have at least one 'qoqa_id'
    # in variants, the automatic generation of variants should raise an error

    is_wine = fields.Boolean(string='Wine',
                             default=False)
    is_liquor = fields.Boolean(string='Liquor',
                               default=False)

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

    # used to generate the variants default_code
    base_default_code = fields.Char(
        string='Base Reference',
        help="All generated variants' internal code will begin with this code."
    )
    default_code = fields.Char(
        compute='_compute_default_code',
        inverse='_inverse_default_code',
        store=True,
    )

    @api.depends('product_variant_ids.default_code', 'base_default_code')
    def _compute_default_code(self):
        for record in self:
            if record.base_default_code:
                record.default_code = record.base_default_code
            elif record.product_variant_ids:
                first = record.product_variant_ids[0]
                record.default_code = first.default_code

    @api.multi
    def _inverse_default_code(self):
        for record in self:
            # when we write on a default code and we are not in a
            # multi-variant, propagate the default code to the "unique variant"
            if record.product_variant_count == 1:
                record.product_variant_ids.default_code = record.default_code

    @api.onchange('default_code')
    def _onchange_qoqa_product_default_code(self):
        if self.default_code and not self.base_default_code:
            self.base_default_code = self.default_code


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # We set the default_code required in views and not in db, so we do compute
    # the default code for variants after they have been inserted in db
    # which is easier to read linked attribute values

    @api.model
    def create(self, vals):
        record = super(ProductProduct, self).create(vals)
        record.set_default_code()
        return record

    @api.multi
    def set_default_code(self):
        for record in self:
            if not record.attribute_value_ids:
                continue
            attr_values = record.attribute_value_ids.sorted(
                lambda av: (av.attribute_id.sequence, av.attribute_id.id)
            )
            base = record.product_tmpl_id.base_default_code or ''
            default_code = u' - '.join(
                [base] + [val.code or val.name for val in attr_values]
            )
            record.default_code = default_code


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char(string='Code')
