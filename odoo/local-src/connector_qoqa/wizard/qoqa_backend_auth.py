# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, exceptions, _

from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from ..qoqa_backend.common import AuthAdapter
from ..exception import QoQaAPIAuthError


class QoqaBackendAuth(models.TransientModel):
    """ Wizard to get the token access.  """
    _name = 'qoqa.backend.auth'
    _description = 'QoQa Backend Token Auth Wizard'

    backend_id = fields.Many2one(
        comodel_name='qoqa.backend',
        string='QoQa Backend',
        default=lambda self: self._default_backend_id(),
        required=True,
    )
    login = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True)

    @api.model
    def _default_backend_id(self):
        if self.env.context.get('active_model') != 'qoqa.backend':
            return
        backend_id = self.env.context.get('active_id')
        if not backend_id:
            return
        return backend_id

    @api.multi
    def auth(self):
        """ Request the authorization token from the API,

        using the login and the password. We then store the token in the
        backend and forget the login and password (when the wizard's record is
        deleted by Odoo).

        """
        self.ensure_one()
        session = ConnectorSession.from_env(self.env)
        with get_environment(session,
                             'qoqa.backend',
                             self.backend_id.id) as connector_env:
            auth = connector_env.get_connector_unit(AuthAdapter)
            auth.client.token = ''
            try:
                token = auth.authenticate(self.login, self.password)
            except QoQaAPIAuthError as err:
                raise exceptions.UserError(
                    _('Authentication failed:\n\n%s') % (err,)
                )
            self.backend_id.write({
                'token': token,
            })
