# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import logging
from openerp import _
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.unit.synchronizer import Exporter
from ..connector import get_environment
from ..backend import qoqa
from ..related_action import unwrap_binding

_logger = logging.getLogger(__name__)


@qoqa
class CancelSalesOrder(Exporter):
    _model_name = 'qoqa.sale.order'

    def run(self, binding_id):
        """ Cancel a sales order on QoQa"""
        qoqa_id = self.binder.to_backend(binding_id)
        if not qoqa_id:
            return _('Sales order does not exist on QoQa')
        self.backend_adapter.cancel(qoqa_id)
        return _('Sales order canceled on QoQa')


@qoqa
class SettleSalesOrder(Exporter):
    _model_name = 'qoqa.sale.order'

    def run(self, binding_id):
        """ Settle a sales order on QoQa"""
        qoqa_id = self.binder.to_backend(binding_id)
        if not qoqa_id:
            return _('Sales order does not exist on QoQa')
        self.backend_adapter.settle(qoqa_id)
        return _('Sales order settled on QoQa')


@job(default_channel='root.connector_qoqa.fast')
@related_action(action=unwrap_binding)
def cancel_sales_order(session, model_name, record_id):
    """ Cancel a Sales Order """
    binding = session.env[model_name].browse(record_id)
    backend_id = binding.backend_id.id
    with get_environment(session, model_name, backend_id) as connector_env:
        canceler = connector_env.get_connector_unit(CancelSalesOrder)
        return canceler.run(record_id)


@job(default_channel='root.connector_qoqa.normal')
@related_action(action=unwrap_binding)
def settle_sales_order(session, model_name, record_id):
    """ Settle a Sales Order """
    binding = session.env[model_name].browse(record_id)
    backend_id = binding.backend_id.id
    with get_environment(session, model_name, backend_id) as connector_env:
        settler = connector_env.get_connector_unit(SettleSalesOrder)
        return settler.run(record_id)
