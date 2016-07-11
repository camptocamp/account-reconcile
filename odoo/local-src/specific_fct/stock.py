# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.addons.base.res.res_partner import _lang_get
import logging

from postlogistics.web_service import PostlogisticsWebServiceQoQa

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
        'Active', default=True,
        help="The active field allows you to hide the picking without "
             "removing it."
    )

    @api.depends('move_lines', 'move_lines.product_qty')
    def _compute_number_of_products(self):
        for picking in self:
            picking.number_of_products = sum(
                picking.mapped('move_lines.product_qty')
            )

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

        for picking in pickings:
            try:
                picking.action_assign()
            except Exception:
                # ignore the error, the picking will just stay as confirmed
                name = picking.name
                _logger.info('error in action_assign for picking %s',
                             name, exc_info=True)
        return True
