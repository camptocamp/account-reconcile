# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA (Nicolas Bessi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api


class VariantGenerator(models.TransientModel):

    _name = 'product_variant_generator'

    @api.multi
    def _get_active_id(self):
        """Boiler plate that check env for active_id"""
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise ValueError('No product_template active id given')
        return active_id

    @api.multi
    def _default_product_template(self):
        """Set the origin product template
        :return: the origin product template id
        """
        return self._get_active_id()

    def _compute_values_for_domain(self):
        """Compute product.attibute.value ids that can be used
        as variant options"""
        values = self._get_related_values_ids()
        self.values_domain_ids = values

    def _default_values_for_domain(self):
        """Compute product.attibute.value ids that can be used
        as variant options"""
        values = self._get_related_values_ids()
        return values.mapped('id')

    def _default_values_for_variants_ids(self):
        """Populate available variants options"""
        return self._get_related_values_ids()

    def _get_related_values_ids(self):
        """Compute product.attibute.value ids that can be used
        as variant options"""
        product_template = self.product_template
        if not product_template:
            product_template_id = self._get_active_id()
            product_template = self.env['product.template'].browse(
                product_template_id)
        ids = product_template.attribute_value_code_ids.mapped('value_id')
        return ids

    product_template = fields.Many2one(
        'product.template',
        string='Source product',
        readonly=True,
        default=_default_product_template
    )

    values_domain_ids = fields.Many2many(
        'product.attribute.value',
        string='Technical domain for values',
        compute=_compute_values_for_domain,
        # compute seems not to be call before write
        # so we have to add a call to defaut
        default=_default_values_for_domain
    )

    values_for_variants_ids = fields.Many2many(
        'product.attribute.value',
        string='Attributes for variant generation',
        default=_default_values_for_variants_ids,
    )

    @api.multi
    def generate_variants(self):
        """ Please refere to
        `qoqa_product.models.product.create_variant_subset_ids'
        """
        self.product_template.create_variant_subset_ids(
            self.values_for_variants_ids
        )
