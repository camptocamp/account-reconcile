# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    active = fields.Boolean(
        'Active', default=True,
        help="The active field allows you to hide the purchase order "
             "without removing it."
    )

    partner_ref = fields.Char(
        states={'done': [('readonly', True)]},
    )

    # TODO: Doit-on le migrer ?
    # Use the module "purchase_group_hooks" in order to
    # redefine one part from purchase order merge: the notes
    # should not be concatenated.

    #def _update_merged_order_data(self, merged_data, order):
        #if order.date_order < merged_data['date_order']:
            #merged_data['date_order'] = order.date_order
        #if order.origin:
            #if (
                #order.origin not in merged_data['origin'] and
                #merged_data['origin'] not in order.origin
            #):
                #merged_data['origin'] = (
                    #(merged_data['origin'] or '') + ' ' + order.origin
                #)
        #return merged_data


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    _order = 'sequence asc, name asc'

    sequence = fields.Integer('Sequence')
