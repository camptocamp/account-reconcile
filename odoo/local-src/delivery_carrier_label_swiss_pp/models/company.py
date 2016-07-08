# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    swiss_pp_stamp_image = fields.Binary(
        'PP Frankling on Post labels',
        help="Stamp with QR code provided by Postbusiness"
        )
