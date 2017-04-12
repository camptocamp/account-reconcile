# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        self_no_track = self.with_context(tracking_disable=True)
        return super(ResPartner, self_no_track).create(vals)

    def init(self, cr):
        # this query is issued every time the list view of partners
        # is displayed
        # SELECT count ( 1 ) FROM "res_partner" WHERE ( ( (
        # "res_partner"."active" = TRUE ) AND (
        # "res_partner"."customer" = TRUE ) ) AND
        # "res_partner"."parent_id" IS NULL );
        index_name = 'res_partner_customer_count_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s '
                       'ON res_partner '
                       '(active, customer, parent_id) '
                       'WHERE active AND customer '
                       'AND parent_id is null ' % index_name)

        # equivalent for the suppliers
        index_name = 'res_partner_supplier_count_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s '
                       'ON res_partner '
                       '(active, customer, parent_id) '
                       'WHERE active AND supplier '
                       'AND parent_id is null ' % index_name)
