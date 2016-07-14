# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.event import on_record_create
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from openerp.addons.connector.exception import MappingError

from ..connector import get_environment
from ..backend import qoqa
from ..related_action import unwrap_binding


@on_record_create(model_names='qoqa.stock.picking')
def delay_export(session, model_name, record_id, vals):
    if session.env.context.get('connector_no_export'):
        return

    record = session.env[model_name].browse(record_id)
    if record.carrier_id:
        export_picking_tracking_done.delay(session, model_name, record_id)


@qoqa
class QoQaTrackingExporter(Exporter):
    _model_name = 'qoqa.stock.picking'

    def _get_qoqa_id(self, binding_name, openerp_id):
        """ Return qoqa_id of this *openerp_id* for which bindind model is
        *binding_name*

        :type binding_name: str
        :type openerp_id: int
        :rtype: str
        """
        binder = self.binder_for(binding_name)
        qoqa_id = binder.to_backend(openerp_id, wrap=True)

        if not qoqa_id:
            raise MappingError(
                'Unable to find binding %s with openerp_id %s'
                % (binding_name, openerp_id)
            )

        return qoqa_id

    def _get_shipping_packages(self, picking_binding):
        # Group the lines per tracking numbers
        packages = {}
        for pack_operation in picking_binding.pack_operation_ids:
            packages.setdefault(pack_operation.result_package_id, set()).add(
                pack_operation
            )

        shipping_packages = []
        for package, operations in packages.iteritems():
            if package:
                number = package.name
            else:
                # if lines are not linked to a tracking, we use the
                # tracking number directly written on the picking
                number = picking_binding.carrier_tracking_ref

            qoqa_package_type_id = None
            if picking_binding.carrier_id:
                qoqa_package_type_id = self._get_qoqa_id(
                    'qoqa.shipper.package.type',
                    picking_binding.carrier_id.id,
                )
            package_dict = {
                'tracking_number': number or "",
                'shipping_package_type_id': qoqa_package_type_id,
            }
            items = []
            for operation in operations:
                items.append({
                    'variation_id': self._get_qoqa_id(
                        'qoqa.product.product', operation.product_id.id
                    ),
                    'quantity': operation.qty_done,
                })

            package_dict['shipping_package_items_attributes'] = items

            shipping_packages.append(package_dict)

        return {'shipping_packages': shipping_packages}

    def run(self, binding_id):
        """ Export the tracking numbers to QoQa """
        picking_binding = self.model.browse(binding_id)
        data = self._get_shipping_packages(picking_binding)

        adapter = self.unit_for(BackendAdapter, 'qoqa.sale.order')
        adapter.add_trackings(
            self._get_qoqa_id('qoqa.sale.order', picking_binding.sale_id.id),
            data
        )

        picking_binding.write({'exported': True})


@job(default_channel='root.connector_qoqa.normal')
@related_action(action=unwrap_binding)
def export_picking_tracking_done(session, model_name, binding_id):
    """ Export trackings of a delivery order. """
    binding = session.env[model_name].browse(binding_id)
    with get_environment(session, model_name,
                         binding.backend_id.id) as connector_env:
        exporter = connector_env.get_connector_unit(QoQaTrackingExporter)
        return exporter.run(binding_id)
