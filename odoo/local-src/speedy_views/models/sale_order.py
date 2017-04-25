# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # revert to the default sort so we can benefit of an index
    # (we remove main_exception_id from the sort)
    _order = 'date_order desc, id desc'

    # often used in searches, 'sales to invoice' menu...
    invoice_status = fields.Selection(index=True)

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
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s '
                       'ON sale_order '
                       '(date_order DESC, id DESC) ' % index_name)

        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'sale_order_active_true_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s ON sale_order '
                       '(active) where active ' % index_name)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_id = fields.Many2one(index=True)
