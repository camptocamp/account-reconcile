# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Deleter
from ..connector import get_environment


class QoQaDeleteSynchronizer(Deleter):
    """ Base deleter for QoQa """

    def run(self, qoqa_id):
        """ Run the synchronization, delete the record on QoQa

        :param qoqa_id: identifier of the record to delete
        """
        self.backend_adapter.delete(qoqa_id)
        return _('Record %s deleted on QoQa') % qoqa_id


@job(default_channel='root.connector_qoqa.normal')
def export_delete_record(session, model_name, backend_id, qoqa_id):
    """ Delete a record on QoQa """
    with get_environment(session, model_name, backend_id) as conn_env:
        deleter = conn_env.get_connector_unit(QoQaDeleteSynchronizer)
        return deleter.run(qoqa_id)
