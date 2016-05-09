# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models
from . company import ResCompany


class SwissPPConfigSettings(models.TransientModel):
    _name = 'swiss_pp.config.settings'
    _inherit = ['res.config.settings', 'abstract.config.settings']

    _companyObject = ResCompany

    _prefix = 'swiss_pp_'
