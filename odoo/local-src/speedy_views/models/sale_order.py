# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models, api, SUPERUSER_ID
from .utils import install_trgm_extension, create_index


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # revert to the default sort so we can benefit of an index
    # (we remove main_exception_id from the sort)
    _order = 'date_order desc, id desc'

    # Separate 2 computes from the main module ; invoice_ids will not be
    # called 4 times during an invoice validation, and storing the invoices
    # link / count on the SO improves the speed on the form view
    @api.depends('name',
                 'order_line.invoice_lines.invoice_id.type',
                 'order_line.invoice_lines.invoice_id.origin',
                 'order_line.invoice_lines.invoice_id.number')
    def _get_invoice_ids(self):
        for order in self:
            invoice_ids = order.order_line.mapped(
                'invoice_lines'
            ).mapped(
                'invoice_id'
            ).filtered(lambda r: r.type in ['out_invoice', 'out_refund'])
            # Search for invoices which have been 'cancelled'
            # (filter_refund = 'modify' in 'account.invoice.refund')
            # use like as origin may contains multiple references
            # (e.g. 'SO01, SO02')
            refunds = invoice_ids.search([('origin', 'like', order.name)])
            invoice_ids |= refunds.filtered(
                lambda r: order.name in [origin.strip() for origin
                                         in r.origin.split(',')]
            )
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                for inv in invoice_ids:
                    refund_ids += refund_ids.search(
                        [('type', '=', 'out_refund'),
                         ('origin', '=', inv.number), ('origin', '!=', False),
                         ('journal_id', '=', inv.journal_id.id)]
                    )

            order.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids
            })

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoiced(self):
        for order in self:
            line_invoice_status = [line.invoice_status for line
                                   in order.order_line]

            if order.state not in ('sale', 'done'):
                invoice_status = 'no'
            elif any(invoice_status == 'to invoice'
                     for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
            elif all(invoice_status == 'invoiced'
                     for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
            elif all(invoice_status in ['invoiced', 'upselling']
                     for invoice_status in line_invoice_status):
                invoice_status = 'upselling'
            else:
                invoice_status = 'no'

            order.update({
                'invoice_status': invoice_status
            })

    invoice_count = fields.Integer(compute='_get_invoice_ids')
    invoice_ids = fields.Many2many(compute='_get_invoice_ids')
    # often used in searches, 'sales to invoice' menu...
    invoice_status = fields.Selection(compute='_get_invoiced', index=True)

    def init(self, cr):

        # default query to display sales orders
        # SELECT "sale_order".id FROM "sale_order" WHERE
        # ( ( ( "sale_order"."active" = TRUE ) AND
        # ( ( "sale_order"."state" NOT IN ( ... ) )
        # OR "sale_order"."state" IS NULL ) ) AND
        # ( "sale_order"."qoqa_shop_id" IN ( ... ) ) )
        # ORDER BY "sale_order"."date_order" DESC,
        # "sale_order"."id" DESC LIMIT 0;
        index_name = 'sale_order_list_sort_desc_index'
        create_index(cr, index_name, self._table,
                     '(date_order DESC, id DESC) ')

        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'sale_order_active_true_index'
        create_index(cr, index_name, self._table, '(active) where active')

        env = api.Environment(cr, SUPERUSER_ID, {})
        trgm_installed = install_trgm_extension(env)
        cr.commit()

        if trgm_installed:
            index_name = 'sale_order_client_order_ref_trgm_index'
            create_index(cr, index_name, self._table,
                         'USING gin (client_order_ref gin_trgm_ops)')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_id = fields.Many2one(index=True)
