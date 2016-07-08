# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class DeliveryCarrier(models.Model):
    """ Add service group """
    _inherit = 'delivery.carrier'

    @api.model
    def _get_carrier_type_selection(self):
        """ Add postlogistics carrier type """
        res = super(DeliveryCarrier, self)._get_carrier_type_selection()
        res.append(('swiss_apost', 'Swiss A Priority'))
        return res

    type = fields.Selection(
        _get_carrier_type_selection, 'Type',
        help="Carrier type (combines several delivery methods)")
