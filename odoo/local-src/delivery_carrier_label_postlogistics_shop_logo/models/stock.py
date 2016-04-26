# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import api, models

from ..postlogistics.web_service import PostlogisticsWebServiceShop


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _generate_postlogistics_label(self, webservice_class=None,
                                      package_ids=None):
        """ Generate post label using shop label """
        if webservice_class is None:
            webservice_class = PostlogisticsWebServiceShop
        return super(StockPicking, self)._generate_postlogistics_label(
            webservice_class=webservice_class,
            package_ids=package_ids)
