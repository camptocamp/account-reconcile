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

        The base url is defined on qoqa backend.
        The path is in ir.config_parameter "backend.user.path"
        The url will be filled with the qoqa user id by replacing "{user_id}"
        or if this string is not present in base url, at the end of the url

        Ex:
        backend_url: www.my_backoffice.com
        backend.user.path: /user/{user_id}
        qoqa_id: 42

        Result:
        www.my_backoffice.com/user/42

        """
        ICP = self.env['ir.config_parameter']
        path = ICP.get_param('backend.user.path')
        if path:
            if '{user_id}' not in path:
                path += '{user_id}'
            for rec in self:
                if not rec.qoqa_bind_ids:
                    continue
                qoqa_rec = rec.qoqa_bind_ids[0]
                backend = qoqa_rec.backend_id
                if not backend or not backend.backend_url:
                    continue
                base_url = backend.backend_url + path
                # ensure it starts with http(s)
                # otherwise using it in link will make it local
                if not base_url.startswith('http'):
                    base_url = 'http://' + base_url
                user_id = qoqa_rec.qoqa_id
                rec.qoqa_url = base_url.format(user_id=user_id)


@qoqa
class ResPartnerAdapter(QoQaAdapter):
    _model_name = 'qoqa.res.partner'
    _endpoint = 'admin/users'
    _resource = 'user'
