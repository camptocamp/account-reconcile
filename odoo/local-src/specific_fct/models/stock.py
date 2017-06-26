# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp
from openerp import api, fields, models
from openerp.addons.base.res.res_partner import _lang_get
import logging

from ..postlogistics.web_service import PostlogisticsWebServiceQoQa

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.
    """
    _inherit = "stock.picking"

    number_of_products = fields.Integer(
        compute='_compute_number_of_products',
        string='Number of products',
        store=True
    )

    lang = fields.Selection(
        related='partner_id.lang',
        string='Language',
        selection=_lang_get,
        readonly=True,
        store=True
    )

    active = fields.Boolean(
        'Active',
        default=True,
        help="The active field allows you to hide the picking without "
             "removing it."
    )

    @api.depends('move_lines', 'move_lines.product_qty')
    def _compute_number_of_products(self):
        for picking in self:
            picking.number_of_products = sum(
                picking.mapped('move_lines.product_qty')
            )

    @api.multi
    def _add_delivery_cost_to_so(self):
        """ We never want to add a delivery line on SO

        The line for the delivery costs is created upfront, not from the
        shipping.
        """
        return

    def _generate_postlogistics_label(self, webservice_class=None,
                                      package_ids=None):
        """ Generate post label using QoQa specific to hide parent name in  """

        return super(StockPicking, self)._generate_postlogistics_label(
            webservice_class=PostlogisticsWebServiceQoQa,
            package_ids=package_ids
        )

    # define domain and better exception catching for cron
    # in stock_picking_mass_assign, in order to use the
    # new field from qoqa_offer, 'sale_create_date'
    @api.multi
    def check_assign_all(self):
        pickings = self
        if not pickings:
            domain = [('picking_type_code', '=', 'outgoing'),
                      ('state', '=', 'confirmed')]
            pickings = self.search(domain, order='sale_create_date')

        count = 0
        total_pickings = len(pickings)
        while pickings:
            pickings_to_assign = pickings[:100]
            pickings = pickings[100:]
            count += 100
            with openerp.registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(
                    new_cr, self.env.uid, self.env.context)
                for picking in pickings_to_assign.with_env(new_env):
                    try:
                        picking.action_assign()
                    except Exception:
                        # ignore the error, the picking will just stay
                        # as confirmed
                        name = picking.name
                        _logger.info('error in action_assign for picking %s',
                                     name, exc_info=True)
                _logger.info('%d / %d pickings done', count, total_pickings)
        return True

    def force_transfer(self, force_qty=True):
        """
            We never want a "partial" batch so we force the qty_done to always
            be equal to product_qty with force_qty=True in force_transfer
        """
        return super(StockPicking, self).force_transfer(force_qty=True)

    def _values_with_carrier_options(self, values):
        values = super(StockPicking, self)._values_with_carrier_options(
            values=values)
        option_ids = values.get('option_ids')
        # Fix to prevent problem when onchange is call
        # the format of the options_ids is wrong
        # we rewrite it
        if option_ids and option_ids[0][1]:
            values.update(option_ids=[(6, 0, [x[1] for x in option_ids])])
        return values


class StockLocation(models.Model):
    _inherit = 'stock.location'

    # Use complete_name for name_get
    @api.multi
    def name_get(self):
        res = []
        for location in self:
            res.append((location.id, location.complete_name))
        return res
