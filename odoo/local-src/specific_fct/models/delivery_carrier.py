# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.model
    def default_get(self, fields_list):
        values = super(DeliveryCarrier, self).default_get(fields_list)
        if 'categ_id' in fields_list:
            if not values.get('categ_id'):
                xmlid = 'specific_fct.product_category_delivery'
                delivery_categ = self.env.ref(xmlid)
                values['categ_id'] = delivery_categ.id
        return values
