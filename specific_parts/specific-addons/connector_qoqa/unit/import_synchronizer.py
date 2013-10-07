# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime
from openerp.tools.translate import _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer
from openerp.addons.connector.exception import IDMissingInBackend
from ..backend import qoqa
from ..connector import get_environment, add_checkpoint

_logger = logging.getLogger(__name__)

"""

Importers for QoQa.

An import can be skipped if the last sync date is more recent than
the last update in QoQa.

They should call the ``bind`` method if the binder even if the records
are already bound, to update the last sync date.

"""

class QoQaImportSynchronizer(ImportSynchronizer):
    """ Base importer for QoQa """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(QoQaImportSynchronizer, self).__init__(environment)
        self.qoqa_id = None
        self.qoqa_record = None

    def _get_qoqa_data(self):
        """ Return the raw QoQa data for ``self.qoqa_id`` """
        return self.backend_adapter.read(self.qoqa_id)

    def _before_import(self):
        """ Hook called before the import, when we have the QoQa
        data"""

    def _is_uptodate(self, binding_id):
        """Return True if the import should be skipped because
        it is already up-to-date in OpenERP"""
        assert self.qoqa_record
        # FIXME: check name of the field
        if not self.qoqa_record.get('updated_at'):
            return  # no update date on QoQa, always import it.
        if not binding_id:
            return  # it does not exist so it shoud not be skipped
        sync_date = self.binder.sync_date(binding_id)
        if not sync_date:
            return
        # FIXME: check name of the field
        qoqa_date = datetime.strptime(self.qoqa_record['updated_at'], fmt)
        # if the last synchronization date is greater than the last
        # update in qoqa, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the qoqa_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in QoQa
        return qoqa_date < sync_date

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        return

    def _map_data(self):
        """ Call the convert on the Mapper so the converted record can
        be obtained using mapper.data or mapper.data_for_create"""
        self.mapper.convert(self.qoqa_record)

    def _validate_data(self, data):
        """ Check if the values to import are correct

        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.

        Raise `InvalidDataError`
        """
        return

    def _get_binding_id(self):
        """Return the binding id from the qoqa id"""
        return self.binder.to_openerp(self.qoqa_id)

    def _create(self, data):
        """ Create the OpenERP record """
        with self.session.change_context({'connector_no_export': True}):
            binding_id = self.session.create(self.model._name, data)
        _logger.debug('%s %d created from QoQa %s',
                      self.model._name, binding_id, self.qoqa_id)
        return binding_id

    def _update(self, binding_id, data):
        """ Update an OpenERP record """
        with self.session.change_context({'connector_no_export': True}):
            self.session.write(self.model._name, binding_id, data)
        _logger.debug('%s %d updated from QoQa %s',
                      self.model._name, binding_id, self.qoqa_id)
        return

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        return

    def run(self, qoqa_id, force=False):
        """ Run the synchronization

        :param qoqa_id: identifier of the record on QoQa
        """
        self.qoqa_id = qoqa_id
        try:
            self.qoqa_record = self._get_qoqa_data()
        except IDMissingInBackend:
            return _('Record does no longer exist in QoQa')
        binding_id = self._get_binding_id()

        if not force and self._is_uptodate(binding_id):
            return _('Already up-to-date.')
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        self._map_data()

        if binding_id:
            record = self.mapper.data
            # special check on data before import
            self._validate_data(record)
            self._update(binding_id, record)
        else:
            record = self.mapper.data_for_create
            # special check on data before import
            self._validate_data(record)
            binding_id = self._create(record)

        self.binder.bind(self.qoqa_id, binding_id)

        self._after_import(binding_id)


class BatchImportSynchronizer(ImportSynchronizer):
    """ The role of a BatchImportSynchronizer is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    def run(self, filters=None):
        """ Run the synchronization """
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, record_id):
        """ Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class DirectBatchImport(BatchImportSynchronizer):
    """ Import the records directly, without delaying the jobs. """
    _model_name = None

    def _import_record(self, record_id):
        """ Import the record directly """
        import_record(self.session,
                      self.model._name,
                      self.backend_record.id,
                      record_id)


class DelayedBatchImport(BatchImportSynchronizer):
    """ Delay import of the records """
    _model_name = None

    def _import_record(self, record_id, **kwargs):
        """ Delay the import of the records"""
        import_record.delay(self.session,
                            self.model._name,
                            self.backend_record.id,
                            record_id,
                            **kwargs)


@qoqa
class TranslationImporter(ImportSynchronizer):
    """ Import translations for a record.

    Usually called from importers, in ``_after_import``.
    For instance from the products and products' categories importers.
    """

    _model_name = []

    def run(self, qoqa_id, binding_id):
        raise NotImplementedError


@qoqa
class AddCheckpoint(ConnectorUnit):
    """ Add a connector.checkpoint on the underlying model
    (not the qoqa.* but the _inherits'ed model) """

    _model_name = ['qoqa.shop',
                   ]

    def run(self, openerp_binding_id):
        binding = self.session.browse(self.model._name,
                                      openerp_binding_id)
        record = binding.openerp_id
        add_checkpoint(self.session,
                       record._model._name,
                       record.id,
                       self.backend_record.id)


@job
def import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from QoQa """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(BatchImportSynchronizer)
    importer.run(filters=filters)


@job
def import_record(session, model_name, backend_id, qoqa_id, force=False):
    """ Import a record from QoQa """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(QoQaImportSynchronizer)
