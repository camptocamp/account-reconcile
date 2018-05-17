# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models, SUPERUSER_ID
from .utils import install_trgm_extension, create_index


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        self_no_track = self.with_context(tracking_disable=True)
        return super(ResPartner, self_no_track).create(vals)

    def init(self, cr):
        env = api.Environment(cr, SUPERUSER_ID, {})
        trgm_installed = install_trgm_extension(env)
        cr.commit()

        if trgm_installed:
            for field in ('name', 'email', 'display_name', 'ref'):
                index_name = 'res_partner_%s_trgm_index' % field
                create_index(cr, index_name, self._table,
                             'USING gin (%s gin_trgm_ops)' % field)

        index_name = 'res_partner_active_index'
        create_index(cr, index_name, self._table, '(active)')

        # this query is issued every time the list view of partners
        # is displayed
        # SELECT count ( 1 ) FROM "res_partner" WHERE ( ( (
        # "res_partner"."active" = TRUE ) AND (
        # "res_partner"."customer" = TRUE ) ) AND
        # "res_partner"."parent_id" IS NULL );
        index_name = 'res_partner_customer_count_index'
        create_index(cr, index_name, self._table,
                     '(active, customer, parent_id) '
                     'WHERE active AND customer '
                     'AND parent_id is null ')

        # equivalent for the suppliers
        index_name = 'res_partner_supplier_count_index'
        create_index(cr, index_name, self._table,
                     '(active, customer, parent_id) '
                     'WHERE active AND supplier '
                     'AND parent_id is null ')
