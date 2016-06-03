# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    unclaimed_initial_categ_id = fields.Many2one(
        comodel_name='crm.case.categ',
        string='Default category for new unclaimed packages'
    )
    unclaimed_first_reminder_categ_id = fields.Many2one(
        comodel_name='crm.case.categ',
        string='Default category for unclaimed packages after first reminder'
    )
    unclaimed_second_reminder_categ_id = fields.Many2one(
        comodel_name='crm.case.categ',
        string='Default category for unclaimed packages after second reminder'
    )
    unclaimed_final_categ_id = fields.Many2one(
        comodel_name='crm.case.categ',
        string='Default category for sent back unclaimed packages'
    )
    unclaimed_stock_journal_id = fields.Many2one(
        comodel_name='stock.journal',
        string='Default stock journal for unclaimed packages'
    )
    unclaimed_invoice_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default journal for invoices for sent back unclaimed packages'
    )
    unclaimed_invoice_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default account for invoices for sent back unclaimed packages'
    )
    unclaimed_invoice_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Default product for invoices for sent back unclaimed packages'
    )
