# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import api, fields, models


class WineCHInventoryWizard(models.TransientModel):
    """Will launch wine CH report and pass required args"""

    _name = "wine.ch.inventory.wizard"
    _description = "Wine CH Report"

    @api.model
    def _default_company(self):
        company_obj = self.env['res.company']
        return company_obj._company_default_get('account.invoice')

    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=_default_company)
    inventory_date = fields.Date('Inventory date')
    location_ids = fields.Many2many('stock.location',
                                    string='Filter on locations')
    beverage_type = fields.Selection(
        [('wine', "Wine"),
         ('liquor', "Liquor")],
        "Beverage type",
        default='wine')

    @api.multi
    def print_inventory_report(self, data):
        data['form'] = self.read(['inventory_date',
                                  'location_ids',
                                  'beverage_type'],
                                 )[0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'wine_ch_report.report_wine_inventory',
                'datas': data}

    @api.multi
    def print_cscv_form_report(self, data):
        data['form'] = self.read(['inventory_date',
                                  'location_ids',
                                  'beverage_type'],
                                 )[0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'wine_ch_report.report_wine_cscv_form',
                'datas': data}
