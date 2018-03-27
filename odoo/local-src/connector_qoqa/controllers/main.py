"""
Receive calls from QoQa web and create jobs that will create or
update the local records with the content of the request.

Change a sales order shipping address

$ curl -i -X POST \
   -H "Content-Type:application/json" \
   -H "Cookie:session_id=0822d81781d248e7a8e556be2eb5c3b1d98e3408" \
   -d \
'{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "call",
    "params": {
        "order_id": 4268735,
        "address": {
            "data": {
                "attributes": {
                    "service": "standard",
                    "city": "Hauterive",
                    "kind": "personal",
                    "user_id": 4545,
                    "order_user_id": null,
                    "zip": "2068",
                    "firstname": "John",
                    "alias": null,
                    "lastname": "Doe",
                    "street2": null,
                    "country_id": 1,
                    "service_client_number": null,
                    "updated_at": "2016-06-28T17:32:24.000+02:00",
                    "phone": "0781733455",
                    "street": "Chemin du bois 17",
                    "company_name": null,
                    "gender": 1,
                    "country": "Suisse",
                    "digicode": null,
                    "created_at": "2016-06-28T17:32:24.000+02:00"
                },
                "type": "address",
                "id": "900000001"
            }
        }
    }
}
' \
 'http://localhost/connector_qoqa/sale/change_shipping_address'

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
