# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, fields, models, _
from openerp.exceptions import UserError


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
        if vals.get('attribute_line_ids'):
            # Add the variable to the context to "skip" variant creation
            result = super(ProductTemplate, self.with_context(
                create_product_variant=True)).create(vals)
        else:
            # We don't have attributes, so we want to generate a variant
            result = super(ProductTemplate, self).create(vals)
        # Fill value codes
        result.fill_value_codes()
        return result

    @api.multi
    def write(self, vals):
        for template in self:
            if (
                (
                    'attribute_line_ids' in vals and
                    vals.get('attribute_line_ids')
                )
                or
                (
                    'attribute_line_ids' not in vals and
                    template.attribute_line_ids
                )
            ):
                # Add the variable to the context to "skip" variant creation
                super(ProductTemplate, template.with_context(
                    create_product_variant=True)).write(vals)
            else:
                # We don't have attributes, so we want to generate a variant
                super(ProductTemplate, template).write(vals)
                if 'default_code' in vals:
                    template.product_variant_ids.write({
                        'default_code': vals['default_code']
                    })
        # Fill value codes
        self.fill_value_codes()
        return True

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

    def _product_exists(self, template, values):
        """Predicate that test if a variant exists

        :param template: product.template record
              on which variants should exists
        :param values: recordset of product.attribue.value
              which should represent a variant
        """
        request = """SELECT att_id FROM
                      product_attribute_value_product_product_rel
                      WHERE prod_id = %s"""
        cr = self.env.cr
        cr.execute(request, (template.id,))
        att_ids = cr.fetchall()
        att_ids = set([x[0] for x in att_ids])
        return set(x.id for x in values) == att_ids

    def create_variant_subset_ids(self, values_subset):
        """Create a subset of all variants filtered by the given value_subset.
        If a variant proposed by the subset is already present we simply sckip
        the creation of the variant.

        As we are working on a subset we can not
        detect if a variant must be deleted

        From an implementation point of view, we do not override the original
        `product.template.create_variant_ids` using named args detection.
        It is not yet mandatory and we do not want to introduce unexpected
        side effects.

        :param values_subset: recordset of product.attribue.value
            for wich we want to create variants
        """
        # We keep this context update in order
        # to allows a later create_variant_ids direct override
        if self.env.context.get("create_product_variant"):
            return None
        self = self.with_context(active_test=False,
                                 create_product_variant=True)
        product_obj = self.env["product.product"]
        for tmpl in self:
            # list of values combination
            variant_alone = []
            all_variants = [[]]
            for variant in tmpl.attribute_line_ids:
                values = variant.value_ids & values_subset
                if len(values) == 1:
                    variant_alone.append(values[0])
                temp_variants = []
                for variant in all_variants:
                    for value in values:
                        temp_variants.append(sorted(variant + [value]))
                        continue
                if temp_variants:
                    all_variants = temp_variants

            # adding an attribute with only one
            # value should not recreate product
            # write this attribute on every product
            # to make sure we don't lose them
            for variant in variant_alone:
                products = product_obj
                for product in tmpl.product_variant_ids:
                    prod_attrs = product.mapped(
                        'attribute_value_ids.attribute_id')
                    if not variant.attribute_id <= prod_attrs:
                        products |= product
                products.write({'attribute_value_ids': [(4, variant.id)]})
            # check product
            variants_to_activate = product_obj
            for product in tmpl.product_variant_ids:
                variants = sorted(product.attribute_value_ids)
                if variants in all_variants:
                    all_variants.pop(all_variants.index(variants))
                    if not product.active:
                        variants_to_activate |= product
            if variants_to_activate:
                variants_to_activate.write({'active': True})

            # create new product
            for variants in all_variants:
                if self._product_exists(tmpl, variants):
                    continue
                values = {
                    'product_tmpl_id': tmpl.id,
                    'attribute_value_ids': [(6, 0, [x.id for x in variants])]
                }
                product_obj.create(values)

        return True


class ProductProduct(models.Model):
    _inherit = 'product.product'

    seller_price = fields.Float(
        string='Supplier Price',
        compute='_compute_seller_price',
        inverse='_inverse_seller_price',
        store=True,
    )

    @api.depends('variant_seller_ids.price',
                 'product_tmpl_id.seller_ids.price')
    def _compute_seller_price(self):
        for record in self:
            supplierinfo = record.variant_seller_ids
            if len(supplierinfo) == 1 and supplierinfo[0].price:
                record.seller_price = supplierinfo[0].price
            else:
                supplierinfo = record.tmpl_seller_ids
                if len(supplierinfo) == 1 and supplierinfo[0].price:
                    record.seller_price = supplierinfo[0].price
                else:
                    record.seller_price = False

    def _inverse_seller_price(self):
        for record in self:
            # Update supplierinfo if any
            supplierinfo = record.variant_seller_ids
            if len(supplierinfo) == 1:
                supplierinfo.write({'price': record.seller_price})
            else:
                # Else create supplierinfo using template data if any
                tmpl_supplierinfo = record.tmpl_seller_ids
                if len(tmpl_supplierinfo) == 1:
                    tmpl_supplierinfo.copy({
                        'product_id': record.id,
                        'price': record.seller_price,
                    })
                else:
                    raise UserError(_(
                        'Failed setting variant supplier price because no '
                        'single supplier info are available either for the '
                        'variant or the product template.'
                    ))

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
