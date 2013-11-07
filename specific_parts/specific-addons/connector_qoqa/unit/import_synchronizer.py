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
from openerp.addons.connector.unit.mapper import ImportMapper
from openerp.addons.connector.exception import IDMissingInBackend
from ..backend import qoqa
from ..connector import (get_environment,
                         add_checkpoint,
                         iso8601_to_utc_datetime
                         )

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
        qoqa_updated_at = self.qoqa_record.get('updated_at')
        if not qoqa_updated_at:
            return  # no update date on QoQa, always import it.
        qoqa_date = iso8601_to_utc_datetime(qoqa_updated_at)
        if not binding_id:
            return  # it does not exist so it shoud not be skipped
        sync_date = self.binder.sync_date(binding_id)
        if not sync_date:
            return
        # if the last synchronization date is greater than the last
        # update in qoqa, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the qoqa date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in QoQa
        return qoqa_date < sync_date

    def _import_dependency(self, qoqa_id, binding_model,
                           importer_class=None):
        """
        Import a dependency. The importer class is a subclass of
        ``QoQaImportSynchronizer``. A specific class can be defined.

        :param qoqa_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_cls: :py:class:`openerp.addons.connector.connector.ConnectorUnit`
                             class or parent class to use for the export.
                             By default: QoQaImportSynchronizer
        :type importer_cls: :py:class:`openerp.addons.connector.connector.MetaConnectorUnit`
        """
        if not qoqa_id:
            return
        if importer_class is None:
            importer_class = QoQaImportSynchronizer
        binder = self.get_binder_for_model(binding_model)
        if binder.to_openerp(qoqa_id) is None:
            importer = self.get_connector_unit_for_model(
                importer_class, model=binding_model)
            importer.run(qoqa_id)

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

    def run(self, from_date=None):
        """ Run the synchronization """
        record_ids = self.backend_adapter.search(from_date=from_date)
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

    _model_name = ['qoqa.product.template',
                   'qoqa.product.product',
                   'qoqa.offer',
                   ]

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(TranslationImporter, self).__init__(environment)
        self.record = self.binding_id = None
        self.mapper_class = ImportMapper

    def _translate(self, lang):
        assert self.record
        assert self.binding_id
        session = self.session
        fields = self.model.fields_get(session.cr, session.uid,
                                       context=session.context)
        # find the translatable fields of the model
        translatable_fields = [field for field, attrs in fields.iteritems()
                               if attrs.get('translate')]
        mapper = self.get_connector_unit_for_model(self.mapper_class)
        mapper.lang = lang
        mapper.convert(self.record)
        record = mapper.data
        data = dict((field, value) for field, value in record.iteritems()
                    if field in translatable_fields)

        ctx = {'connector_no_export': True, 'lang': lang.code}
        with session.change_context(ctx):
            session.write(self.model._name, self.binding_id, data)

    def run(self, record, binding_id, mapper=None):
        self.record = record
        self.binding_id = binding_id
        if mapper is not None:
            self.mapper_class = mapper
        session = self.session

        if not record.get('translations'):
            return
        for tr_record in record['translations']:
            lang_binder = self.get_binder_for_model('res.lang')
            lang_id = lang_binder.to_openerp(tr_record['language_id'],
                                             unwrap=True)
            if lang_id == self.backend_record.default_lang_id.id:
                continue
            lang = session.browse('res.lang', lang_id)
            self._translate(lang)


@qoqa
class AddCheckpoint(ConnectorUnit):
    """ Add a connector.checkpoint on the underlying model
    (not the qoqa.* but the _inherits'ed model) """

    _model_name = ['qoqa.shop',
                   'qoqa.product.template',
                   'qoqa.product.product',
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
def import_batch(session, model_name, backend_id):
    """ Prepare a batch import of records from QoQa """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(BatchImportSynchronizer)
    importer.run()


@job
def import_batch_from_date(session, model_name, backend_id, from_date=None):
    """ Prepare a batch import of records from QoQa """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(BatchImportSynchronizer)
    importer.run(from_date=from_date)


@job
def import_record(session, model_name, backend_id, qoqa_id, force=False):
    """ Import a record from QoQa """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(QoQaImportSynchronizer)
    importer.run(qoqa_id, force=force)
