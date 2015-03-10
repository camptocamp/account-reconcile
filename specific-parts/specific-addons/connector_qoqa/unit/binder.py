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

from datetime import datetime
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from openerp.addons.connector.connector import Binder
from ..backend import qoqa


class QoQaBinder(Binder):
    """ Generic Binder for QoQa """

    _sync_date_field = None

    def sync_date(self, binding_id):
        assert self._sync_date_field
        if isinstance(binding_id, orm.browse_record):
            binding = binding_id
        else:
            binding = self.session.read(self.model._name,
                                        binding_id,
                                        [self._sync_date_field])
        sync_date = binding[self._sync_date_field]
        if not sync_date:
            return
        fmt = DEFAULT_SERVER_DATETIME_FORMAT
        return datetime.strptime(sync_date, fmt)


@qoqa
class QoQaNoneBinder(QoQaBinder):
    """ Always return None ids.

    Used as instance for the models which are the options
    of product custom attributes but should not be exported.

    The export of the products will send the key but with
    an empty value to QoQa. QoQa ignores the attributes it
    doesn't know.
    """
    _model_name = ['wine.class']

    def to_openerp(self, external_id, unwrap=False):
        return None

    def to_backend(self, binding_id, wrap=False):
        return None

    def bind(self, external_id, binding_id):
        raise TypeError('%s cannot be synchronized' % self.model._name)


# TODO: seems to be a ByAnyFieldBinder with 'qoqa_id' as matcher
@qoqa
class QoQaDirectBinder(QoQaBinder):
    """
    Bindings are done directly on the model, the ``qoqa_id`` field in
    the model contains the ID on QoQa. This is possible because we have
    only 1 QoQa Backend. This is preferred when there is no synchronization
    of the models.
    Example: the ``qoqa_id`` on the company is setup manually once, there
    is no import of export of the companies, but we need its ID to link
    the ``qoqa.shop`` to the correct company.
    """
    _model_name = ['qoqa.offer',
                   'qoqa.offer.position',
                   'qoqa.offer.position.variant',
                   'qoqa.buyphrase',
                   ]
    _sync_date_field = 'qoqa_sync_date'

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: No effect in the direct binding
        :return: ID of the record in OpenERP
                 or None if the external_id is not mapped
        :rtype: int
        """
        with self.session.change_context(dict(active_test=False)):
            binding_ids = self.session.search(
                self.model._name,
                [('qoqa_id', '=', str(external_id))])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        return binding_ids[0]

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        Wrap is not applicable for this binder because the binded record
        is the same than the binding record.

        :param binding_id: OpenERP ID for which we want the external id
        :param wrap: if True, the value passed in binding_id is the ID of the
                     binded record, not the binding record.
        :return: backend identifier of the record
        """
        qoqa_record = self.session.read(self.model._name,
                                        binding_id,
                                        ['qoqa_id'])
        assert qoqa_record
        qoqa_id = qoqa_record['qoqa_id']
        if not qoqa_id:  # prefer None over False
            return None
        return qoqa_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # avoid to trigger the export when we modify the `qoqa_id`
        with self.session.change_context({'connector_no_export': True}):
            with self.session.change_user(SUPERUSER_ID):
                self.session.write(
                    self.model._name,
                    binding_id,
                    {'qoqa_id': str(external_id),
                     self._sync_date_field: now_fmt})


@qoqa
class QoQaInheritsBinder(QoQaBinder):
    """
    Bindings are done directly on the binding model.

    Binding models are models called ``qoqa.{normal_model}``,
    like ``qoqa.res.partner`` or ``qoqa.product.product``.
    They ``_inherits`` from the normal models and contains
    the QoQa ID, the ID of the QoQa Backend and the additional
    fields belonging to the QoQa instance.
    """
    _model_name = ['qoqa.shop',
                   'qoqa.product.template',
                   'qoqa.product.product',
                   'qoqa.res.partner',
                   'qoqa.address',
                   'qoqa.sale.order',
                   'qoqa.sale.order.line',
                   'qoqa.accounting.issuance',
                   'qoqa.promo.issuance.line',
                   'qoqa.voucher.issuance.line',
                   ]
    _sync_date_field = 'sync_date'

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: if True, returns the openerp_id of the qoqa_xxxx record,
                       else return the id (binding id) of that record
        :return: a record ID, depending on the value of unwrap,
                 or None if the external_id is not mapped
        :rtype: int
        """
        with self.session.change_context(dict(active_test=False)):
            binding_ids = self.session.search(
                self.model._name,
                [('qoqa_id', '=', str(external_id)),
                 ('backend_id', '=', self.backend_record.id)])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        binding_id = binding_ids[0]
        if unwrap:
            return self.session.read(self.model._name,
                                     binding_id,
                                     ['openerp_id'])['openerp_id'][0]
        else:
            return binding_id

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        :param binding_id: OpenERP ID for which we want the external id
        :param wrap: if True, the value passed in binding_id is the ID of the
                     bound record, not the binding record.
        :return: backend identifier of the record
        """
        if wrap:
            with self.session.change_context(dict(active_test=False)):
                binding_id = self.session.search(
                    self.model._name,
                    [('openerp_id', '=', binding_id),
                     ('backend_id', '=', self.backend_record.id)])
            if binding_id:
                binding_id = binding_id[0]
            else:
                return None
        qoqa_record = self.session.read(self.model._name,
                                        binding_id,
                                        ['qoqa_id'])
        assert qoqa_record
        qoqa_id = qoqa_record['qoqa_id']
        if not qoqa_id:  # prefer None over False
            return None
        return qoqa_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # avoid to trigger the export when we modify the `qoqa_id`
        with self.session.change_context({'connector_no_export': True}):
            with self.session.change_user(SUPERUSER_ID):
                values = {'qoqa_id': str(external_id),
                          self._sync_date_field: now_fmt}
                self.session.write(self.model._name, binding_id, values)


class ByAnyFieldBinder(QoQaBinder):
    """
    The binding is matched using a field (example: a code).

    There is no synchro, so no ``sync()`` method.

    The ``_matching_field`` should be implemented in sub-classes.

    It assumes that there is only 1 QoQa Backend and therefore it
    searches for the first record whose field match with the external
    id.
    """
    _model_name = None
    _matching_field = None

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(ByAnyFieldBinder, self).__init__(environment)
        if self._matching_field is None:
            raise TypeError('_matching_field not defined')

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: No effect in the direct binding
        :return: ID of the record in OpenERP
                 or None if the external_id is not mapped
        :rtype: int
        """
        with self.session.change_context(dict(active_test=False)):
            binding_ids = self.session.search(
                self.model._name,
                [(self._matching_field, '=', str(external_id))])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        return binding_ids[0]

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        :param binding_id: OpenERP ID for which we want the external id
        :param wrap: if True, the value passed in binding_id is the ID of the
                     binded record, not the binding record.
        :return: backend identifier of the record
        """
        qoqa_record = self.session.read(self.model._name,
                                        binding_id,
                                        [self._matching_field])
        assert qoqa_record
        qoqa_id = qoqa_record[self._matching_field]
        if not qoqa_id:  # prefer None over False
            return None
        return qoqa_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        raise TypeError('This type of binding is not synchronized')
