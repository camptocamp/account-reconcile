# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaResPartner(models.Model):
    _name = 'qoqa.res.partner'
    _inherit = 'qoqa.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'QoQa User'

    openerp_id = fields.Many2one(comodel_name='res.partner',
                                 string='Customer',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    qoqa_name = fields.Char(string='QoQa Name')
    qoqa_active = fields.Boolean(string='QoQa Active')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.res.partner',
        inverse_name='openerp_id',
        copy=False,
        string='QBindings')

    qoqa_url = fields.Char(
        compute="_compute_qoqa_url"
    )

    @api.multi
    def _compute_qoqa_url(self):
        """ Generate direct access link to backoffice user page

        The base url is defined in ir.config_parameter "backoffice.user.url"
        The url will be filled with the qoqa user id by replacing "{user_id}"
        or if this string is not present in base url, at the end of the url

        Ex: www.my_backoffice.com/user/{user_id}

        """
        ICP = self.env['ir.config_parameter']
        base_url = ICP.get_param('backoffice.user.url')
        if base_url:
            if '{user_id}' not in base_url:
                base_url += '{user_id}'
            # ensure it starts with http(s)
            # otherwise using it in link will make it local
            if not base_url.startswith('http'):
                base_url = 'http://' + base_url
            for rec in self:
                if rec.qoqa_bind_ids:
                    user_id = rec.qoqa_bind_ids[0].qoqa_id
                    rec.qoqa_url = base_url.format(user_id=user_id)


@qoqa
class ResPartnerAdapter(QoQaAdapter):
    _model_name = 'qoqa.res.partner'
    _endpoint = 'admin/users'
    _resource = 'user'
