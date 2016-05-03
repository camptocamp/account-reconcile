# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    qoqa_type = fields.Selection(
        selection=[('service', 'Service'),
                   ('rate', 'Rate')],
        string='Type on QoQa',
    )
