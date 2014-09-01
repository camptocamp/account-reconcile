# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Joel Grand-Guillaume
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp.osv.orm import Model
from osv import fields

import decimal_precision as dp
_logger = logging.getLogger(__name__)


class qoqa_offer(Model):
    _inherit = 'qoqa.offer'

    def _compute_margin(self, cr, uid, ids, field_names, arg, context=None):
        """
        Compute the absolute and relativ margin based on price without
        tax, and always in company currency. We exclude the (in_invoice,
        in_refund) from the computation as we only want to see in the
        offer form the margin made on our sales.
        The base calculation is made from the informations stored in the
        invoice line of paid and open invoices.
        We return 999 as relativ margin if no sale price is define. We
        made that choice to differenciate the 0.0 margin from null !

        :return dict of dict of the form:
            {INT Product ID : {
                    float margin_absolute,
                    float margin_relative
                    float subtotal_company
                    float subtotal_cost_price_company
                    }}
        """
        res = {}
        tot_sale = {}
        tot_cost = {}
        if context is None:
            context = {}
        if not ids:
            return res
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        company_id = user.company_id.id
        for offer_id in ids:
            res[offer_id] = {
                'margin_absolute': 0,
                'margin_relative': 0,
                'subtotal_company': 0,
                'subtotal_cost_price_company': 0}
            tot_sale[offer_id] = 0
            tot_cost[offer_id] = 0
        # get information about invoice lines relative to our products
        # belonging to open or paid invoices in the considered period
        query = '''
        SELECT inv.offer_id, type,
              SUM(subtotal_cost_price_company),
              SUM(subtotal_company)
        FROM account_invoice_line AS line
        INNER JOIN account_invoice AS inv ON (inv.id = line.invoice_id)
        WHERE %s inv.state IN ('open', 'paid')
          AND type NOT IN ('in_invoice', 'in_refund')
          AND inv.offer_id IN %%(offer_ids)s
          AND inv.company_id = %%(company_id)s
        GROUP BY inv.offer_id, type
        HAVING SUM(subtotal_cost_price_company) != 0
          AND SUM(subtotal_company) != 0
        '''
        substs = context.copy()
        substs.update(
            offer_ids=tuple(res),
            company_id=company_id
            )
        date_clause = []
        if 'from_date' in substs:
            date_clause.append('inv.date_invoice >= %(from_date)s AND')
        if 'to_date' in substs:
            date_clause.append('inv.date_invoice <= %(to_date)s AND')
        query %= ' '.join(date_clause)
        cr.execute(query, substs)
        for offer_id, inv_type, cost, sale in cr.fetchall():
            res[offer_id]['margin_absolute'] += (sale - cost)
            res[offer_id]['subtotal_company'] += sale
            res[offer_id]['subtotal_cost_price_company'] += cost
            tot_sale[offer_id] += sale
        for offer_id in tot_sale:
            if tot_sale[offer_id] == 0:
                _logger.debug("Sale price for product ID %d is 0, "
                              "cannot compute margin rate...", offer_id)
                res[offer_id]['margin_relative'] = 999.
            else:
                absolute_margin = res[offer_id]['margin_absolute']
                total = tot_sale[offer_id]
                relative_margin = (absolute_margin / total) * 100
                res[offer_id]['margin_relative'] = relative_margin
        return res

    _columns = {
        'subtotal_company': fields.function(
            _compute_margin,
            readonly=True, type='float',
            string='Net Sales',
            multi='product_historical_margin',
            digits_compute=dp.get_precision('Sale Price'),
            help="The subtotal net sales of all invoice lines linked to "
                 "this offer."),
        'subtotal_cost_price_company': fields.function(
            _compute_margin,
            readonly=True, type='float',
            string='Cost',
            multi='product_historical_margin',
            digits_compute=dp.get_precision('Sale Price'),
            help="The cost subtotal of all invoice lines "
                 "linked to this offer."),
        'margin_absolute': fields.function(
            _compute_margin,
            readonly=True, type='float',
            string='Real Margin',
            multi='product_historical_margin',
            digits_compute=dp.get_precision('Sale Price'),
            help="The Real Margin [ sale price - cost price ] "
                 "of the product in absolute value "
                 "based on historical values computed from open "
                 "and paid invoices."),
        'margin_relative': fields.function(
            _compute_margin,
            readonly=True, type='float',
            string='Real Margin (%)',
            multi='product_historical_margin',
            digits_compute=dp.get_precision('Sale Price'),
            help="The Real Margin [ Real Margin / sale price ] "
                 "of the product in relative value "
                 "based on historical values computed from open "
                 "and paid invoices."
                 "If no real margin set, will display 999.0 "
                 "(if not invoiced yet for example)."),
        }
