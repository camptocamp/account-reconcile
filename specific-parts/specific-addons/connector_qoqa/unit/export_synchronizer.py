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
from contextlib import contextmanager
from datetime import datetime
import psycopg2
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.exception import RetryableJobError
from .import_synchronizer import import_record
from ..connector import get_environment
from ..backend import qoqa

_logger = logging.getLogger(__name__)


"""

Exporters for QoQa.

In addition to its export job, an exporter has to:

* check in QoQa if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""


class QoQaBaseExporter(ExportSynchronizer):
    """ Base exporter for QoQa """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(QoQaBaseExporter, self).__init__(environment)
        self.binding_id = None
        self.qoqa_id = None

    def _delay_import(self):
        """ Schedule an import of the record.

        Adapt in the sub-classes when the model is not imported
        using ``import_record``.
        """
        # force is True because the sync_date will be more recent
        # so the import would be skipped if it was not forced
        assert self.qoqa_id
        import_record.delay(self.session, self.model._name,
                            self.backend_record.id, self.qoqa_id,
                            force=True)

    def _should_import(self):
        """ Before the export, compare the update date
        in QoQa and the last sync date in OpenERP,
        if the former is more recent, schedule an import
        to not miss changes done in QoQa.
        """
        assert self.binding_record
        if not self.qoqa_id:
            return False
        sync = self.binding_record.sync_date
        if not sync:
            return True
        record = self.backend_adapter.read(self.qoqa_id,
                                           attributes=['updated_at'])

        fmt = DEFAULT_SERVER_DATETIME_FORMAT
        sync_date = datetime.strptime(sync, fmt)
        qoqa_date = datetime.strptime(record['updated_at'], fmt)
        return sync_date < qoqa_date

    def _get_openerp_data(self):
        """ Return the raw OpenERP data for ``self.binding_id`` """
        return self.session.browse(self.model._name, self.binding_id)

    def run(self, binding_id, *args, **kwargs):
        """ Run the synchronization

        :param binding_id: identifier of the binding record to export
        """
        self.binding_id = binding_id
        self.binding_record = self._get_openerp_data()

        self.qoqa_id = self.binder.to_backend(self.binding_id)

        result = self._run(*args, **kwargs)

        self.binder.bind(self.qoqa_id, self.binding_id)
        # commit so we keep the external ID if several exports
        # are called and one of them fails
        self.session.commit()
        return result

    def _run(self):
        """ Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError


class QoQaExporter(QoQaBaseExporter):
    """ A common flow for the exports to QoQa """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(QoQaExporter, self).__init__(environment)
        self.binding_record = None

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        return False

    @contextmanager
    def _retry_unique_violation(self):
        """ Context manager: catch Unique constraint error and retry the
        job later.

        When we execute several jobs workers concurrently, it happens
        that 2 jobs are creating the same record at the same time (binding
        record created by :meth:`_export_dependency`), resulting in:

            IntegrityError: duplicate key value violates unique
            constraint "qoqa_product_template_openerp_uniq"
            DETAIL:  Key (backend_id, openerp_id)=(1, 4851) already exists.

        In that case, we'll retry the import just later.

        """
        try:
            yield
        except psycopg2.IntegrityError as err:
            if err.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise RetryableJobError(
                    'A database error caused the failure of the job:\n'
                    '%s\n\n'
                    'Likely due to 2 concurrent jobs wanting to create '
                    'the same record. The job will be retried later.' % err)
            else:
                raise

    def _export_dependency(self, relation, binding_model,
                           exporter_class=None):
        """
        Export a dependency. The exporter class is a subclass of
        ``QoQaExporter``. If a more precise class need to be defined

        .. warning:: a commit is done at the end of the export of each
                     dependency. The reason for that is that we pushed a record
                     on the backend and we absolutely have to keep its ID.

                     So you *must* take care to not modify the OpenERP database
                     excepted when writing back the external ID or eventual
                     external data to keep on this side.

                     You should call this method only in the beginning of
                     exporter synchronization (in `~._export_dependencies`)
                     and do not write data which should be rollbacked in case
                     of error.

        :param relation: record to export if not already exported
        :type relation: :py:class:`openerp.osv.orm.browse_record`
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param exporter_cls: :py:class:`openerp.addons.connector.\
                                        connector.ConnectorUnit`
                             class or parent class to use for the export.
                             By default: QoQaExporter
        :type exporter_cls: :py:class:`openerp.addons.connector.\
                                       connector.MetaConnectorUnit`
        """
        if not relation:
            return
        if exporter_class is None:
            exporter_class = QoQaExporter
        rel_binder = self.get_binder_for_model(binding_model)
        # wrap is typically True if the relation is a 'product.product'
        # record but the binding model is 'qoqa.product.product'
        wrap = relation._model._name != binding_model

        if wrap and hasattr(relation, 'qoqa_bind_ids'):
            domain = [('openerp_id', '=', relation.id),
                      ('backend_id', '=', self.backend_record.id)]
            with self.session.change_context(dict(active_test=False)):
                binding_ids = self.session.search(binding_model, domain)
            if binding_ids:
                assert len(binding_ids) == 1
                binding_id = binding_ids[0]
            # we are working with a unwrapped record (e.g.
            # product.template) and the binding does not exist yet.
            # Example: I created a product.product and its binding
            # qoqa.product.product, it is exported, but we need to
            # create the binding for the template.
            else:
                ctx = {'connector_no_export': True}
                with self.session.change_context(ctx):
                    with self.session.change_user(SUPERUSER_ID):
                        bind_values = {'backend_id': self.backend_record.id,
                                       'openerp_id': relation.id}
                        # If 2 jobs create it at the same time, retry
                        # one later. A unique constraint (backend_id,
                        # openerp_id) should exist on the binding model
                        with self._retry_unique_violation():
                            binding_id = self.session.create(binding_model,
                                                             bind_values)
                            # Eager commit to avoid having 2 jobs
                            # exporting at the same time.
                            self.session.commit()
        else:
            # If qoqa_bind_ids does not exist we are typically in a
            # "direct" binding (the binding record is the same record).
            # If wrap is True, relation is already a binding record.
            binding_id = relation.id

        if rel_binder.to_backend(binding_id) is None:
            exporter = self.get_connector_unit_for_model(exporter_class,
                                                         binding_model)
            exporter.run(binding_id)

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        return

    def _map_data(self, fields=None):
        """ Returns an instance of
        :py:class:`~openerp.addons.connector.unit.mapper.MapRecord`

        """
        return self.mapper.map_record(self.binding_record)

    def _validate_data(self, data):
        """ Check if the values to import are correct

        Pro-actively check before the ``Model.create`` or
        ``Model.update`` if some fields are missing

        Raise `InvalidDataError`
        """
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_create`.

        QoQa expect that we pass always all the fields, not only
        the modified fields. That's why the `fields` argument
        is None.

        """
        return map_record.values(for_create=True, fields=None, **kwargs)

    def _create(self, data):
        """ Create the QoQa record """
        self._validate_data(data)
        return self.backend_adapter.create(data)

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update`.

        QoQa expect that we pass always all the fields, not only
        the modified fields. That's why the `fields` argument
        is None.

        """
        return map_record.values(fields=None, **kwargs)

    def _update(self, data):
        """ Update an QoQa record """
        assert self.qoqa_id
        self._validate_data(data)
        self.backend_adapter.write(self.qoqa_id, data)

    def _lock(self):
        """ Lock the binding record.

        Lock the binding record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.

        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.

        This behavior works also when the export becomes multilevel
        with :meth:`_export_dependencies`. Each level will set its own lock
        on the binding record it has to export.

        Uses "NO KEY UPDATE", to avoid FK accesses
        being blocked in PSQL > 9.3.
        """
        sql = ("SELECT id FROM %s WHERE ID = %%s FOR NO KEY UPDATE NOWAIT" %
               self.model._table)
        try:
            self.session.cr.execute(sql, (self.binding_id,),
                                    log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info('A concurrent job is already exporting the same '
                         'record (%s with id %s). Job delayed later.',
                         self.model._name, self.binding_id)
            raise RetryableJobError(
                'A concurrent job is already exporting the same record '
                '(%s with id %s). The job will be retried later.' %
                (self.model._name, self.binding_id))

    def _run(self, fields=None):
        """ Flow of the synchronization, implemented in inherited classes.

        `~._export_dependencies` might commit exported ids to the database,
        so please do not do changes in the database before the export of the
        dependencies because they won't be rollbacked.
        """
        assert self.binding_id
        assert self.binding_record

        if not self.qoqa_id:
            fields = None  # should be created with all the fields

        s = self.session
        if not s.pool[self.model._name].exists(s.cr, s.uid,
                                               self.binding_id,
                                               context=s.context):
            return _('Record to export does no longer exist.')

        if self._has_to_skip():
            return

        # export the missing linked resources
        self._export_dependencies()

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data(fields=fields)

        if self.qoqa_id:
            record = self._update_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self._update(record)
        else:
            record = self._create_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self.qoqa_id = self._create(record)
        return _('Record exported with ID %s on QoQa.') % self.qoqa_id


@qoqa
class Translations(ConnectorUnit):
    """ Build a dict ready to use for the Mappings
    with the translations for a model (including the translations
    of the custom attributes if any).
    """
    _model_name = ['qoqa.offer',
                   'qoqa.offer.position',
                   'qoqa.product.product',
                   'qoqa.product.template',
                   'qoqa.buyphrase',
                   ]

    def get_translations(self, record, normal_fields=None,
                         attributes_unit=None, only_langs=None):
        """ The dict will contain:

        * all the translations of ``normal_fields``
        * all the translations of the translatable attributes

        :param record: browse_record of product or template
        :param normal_fields: list of tuples with source and destination
        :param attributes_unit: ConnectorUnit class which respond to
                                ``get_values()`` and return the values
                                of the custom attributes.
        :param only_langs: list of langs to export
        :type only_langs: list of browse_record
        """
        if normal_fields is None:
            normal_fields = []
        if only_langs:
            langs = only_langs
        else:
            lang_ids = self.session.search('res.lang',
                                           [('translatable', '=', True)])
            langs = self.session.browse('res.lang', lang_ids)
        lang_binder = self.get_binder_for_model('res.lang')
        lang_values = []
        for lang in langs:
            qoqa_lang_id = lang_binder.to_backend(lang.id)
            if qoqa_lang_id is None:
                _logger.debug('Language %s skipped for export because '
                              'it has no qoqa_id', lang.code)
                continue
            with self.session.change_context({'lang': lang.code}):
                lang_record = self.session.browse(self.model._name,
                                                  record.id)
            values = {}

            if attributes_unit is not None:
                attrs = self.get_connector_unit_for_model(attributes_unit)
                values.update(attrs.get_values(lang_record, translatable=True))

            for src, target in normal_fields:
                values[target] = lang_record[src]

            values['language_id'] = qoqa_lang_id
            lang_values.append(values)

        return {'translations': lang_values}


@job
def export_record(session, model_name, binding_id, fields=None):
    """ Export a record on QoQa """
    record = session.browse(model_name, binding_id)
    env = get_environment(session, model_name, record.backend_id.id)
    exporter = env.get_connector_unit(QoQaExporter)
    return exporter.run(binding_id, fields=fields)
