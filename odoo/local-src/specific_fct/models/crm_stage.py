# -*- coding: utf-8 -*-
#
# DELETE THIS FILE WHEN `BSQOQ-98` IS CLOSED
#


from openerp import models, api

import traceback
import logging
_logger = logging.getLogger(__name__)


class CrmStage(models.Model):
    """ CRM Stage """
    _inherit = "crm.stage"

    @api.model
    def create(self, vals):
        #
        # DELETE THIS FILE WHEN `BSQOQ-98` IS CLOSED
        #
        _logger.warning(traceback.print_stack())
        return super(CrmStage, self).create(vals)
