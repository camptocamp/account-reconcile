# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import _, api, models
from openerp.exceptions import ValidationError


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.multi
    def unpack_package(self):
        self.ensure_one()
        if self.env.context.get('package') == 'source':
            self.package_id.unpack()
        elif self.env.context.get('package') == 'destination':
            self.result_package_id.unpack()
        else:
            raise ValidationError(_(
                "Unknown package type, please contact Odoo administrator"
            ))
