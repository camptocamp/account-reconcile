# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..backend import qoqa
from ..unit.backend_adapter import QoQaAdapter


class QoqaShop(models.Model):

    _name = 'qoqa.shop'
    _inherit = ['qoqa.shop', 'qoqa.binding']

    qoqa_sync_date = fields.Datetime(
        string='Last synchronization date',
        copy=False,
    )
    identifier = fields.Char()
    domain = fields.Char()
    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.\n"
             "Note that a similar configuration exists for each shop.",
    )


@qoqa
class QoQaShopAdapter(QoQaAdapter):
    _model_name = 'qoqa.shop'
    _endpoint = 'admin/websites'
    _resource = 'website'

    def search(self, filters=None, from_date=None, to_date=None):
        url = self.url()
        payload = {}
        response = self.client.get(url, params=payload)
        records = self._handle_response(response)
        return records['data']
