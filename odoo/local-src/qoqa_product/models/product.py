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
    attribute_value_code_ids = fields.One2many(
        'product.attribute.value.code', 'product_tmpl_id',
        'Product Attribute Codes')

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

    @api.model
    def create(self, vals):
        # Add the variable to the context to "skip" variant creation
        result = super(ProductTemplate, self.with_context(
            create_product_variant=True)).create(vals)
        # Fill value codes
        result.fill_value_codes()
        return result

    @api.multi
    def write(self, vals):
        # Add the variable to the context to "skip" variant creation
        result = super(ProductTemplate, self.with_context(
            create_product_variant=True)).write(vals)
        # Fill value codes
        self.fill_value_codes()
        return result

    @api.multi
    def fill_value_codes(self):
        # Do the difference between the attribute values in
        # product.attribute.line and product.attribute.value.code
        for template in self:
            value_code_obj = self.env['product.attribute.value.code']
            line_values = template.attribute_line_ids.mapped('value_ids')
            code_values = template.attribute_value_code_ids.mapped('value_id')
            new_attr_values = line_values - code_values
            for new_attr_value in new_attr_values:
                value_code_obj.create({
                    'code': False,
                    'value_id': new_attr_value.id,
                    'product_tmpl_id': template.id
                })
            to_delete_attr_values = code_values - line_values
            value_codes_to_delete = value_code_obj.search(
                [('value_id', 'in', to_delete_attr_values.ids),
                 ('product_tmpl_id', '=', template.id)]
            )
            value_codes_to_delete.unlink()


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

            attr_lines = record.product_tmpl_id.attribute_line_ids
            lines_position = {}

            for pos, line in enumerate(attr_lines):
                for value in line.value_ids:
                    lines_position[value] = pos

            attr_values = record.attribute_value_ids.sorted(
                lambda av: (lines_position[av],
                            av.attribute_id.sequence,
                            av.attribute_id.id)
            )
            base = record.product_tmpl_id.base_default_code or ''
            value_codes = dict([
                (vc.value_id.id, vc.code or vc.value_id.name)
                for vc in record.product_tmpl_id.attribute_value_code_ids
            ])
            default_code = u' - '.join(
                [base] + [value_codes[val.id]
                          for val in attr_values]
            )
            record.default_code = default_code


class ProductAttributeValueCode(models.Model):
    _name = 'product.attribute.value.code'
    _order = 'attribute_line_seq'

    code = fields.Char(string='Code')
    value_id = fields.Many2one(
        'product.attribute.value', 'Product Attribute Value',
        required=True, ondelete='cascade')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        required=True, ondelete='cascade')

    attribute_line_seq = fields.Integer(compute='_get_attribute_line_seq',
                                        store=True)

    @api.depends('product_tmpl_id.attribute_line_ids.sequence')
    def _get_attribute_line_seq(self):
        for value_code in self:
            attr_line = value_code.product_tmpl_id.attribute_line_ids.filtered(
                lambda a: a.attribute_id == value_code.value_id.attribute_id)
            value_code.attribute_line_seq = attr_line.sequence


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"
    _order = 'sequence'

    sequence = fields.Integer('Sequence')


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    _order = 'attribute_id_seq,sequence'

    attribute_id_seq = fields.Integer(related='attribute_id.sequence',
                                      store=True)
