"""
Receive calls from QoQa web and create jobs that will create or
update the local records with the content of the request.

Change a sales order shipping address

$ curl -X POST \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc": "2.0", "id": 1, "method": "call", "params": \
             {"sale_id": 4242, "address": {...}}}' \
        http://localhost/connector_qoqa/sale/change_shipping_address

"""

import logging

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import ensure_db

from openerp.addons.connector.session import ConnectorSession

from ..sale.importer import QoQaSaleShippingAddressChanger
from ..connector import get_environment

_logger = logging.getLogger(__name__)


class QoQaController(http.Controller):

    @http.route('/connector_qoqa/sale/change_shipping_address',
                type='json', auth='user', csrf=True)
    def change_shipping_address(self, order_id, address):
        ensure_db()
        backend = request.env['qoqa.backend'].get_singleton()
        session = ConnectorSession.from_env(request.env)
        with get_environment(session, 'qoqa.sale.order',
                             backend.id) as connector_env:
            connector_env.get_connector_unit(
                QoQaSaleShippingAddressChanger
            ).try_change(order_id, address)
