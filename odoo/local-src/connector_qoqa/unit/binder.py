# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from openerp.addons.connector.connector import Binder
from ..backend import qoqa


class QoQaBinder(Binder):
    """ Generic Binder for QoQa """

    _external_field = 'qoqa_id'

    def sync_date(self, binding):
        assert self._sync_date_field
        sync_date = getattr(binding, self._sync_date_field)
        if not sync_date:
            return
        return fields.Datetime.from_string(sync_date)


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
        return self.model.browse()

    def to_backend(self, binding_id, wrap=False):
        return None

    def bind(self, external_id, binding_id):
        raise TypeError('%s cannot be synchronized' % self.model._name)


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
                   'qoqa.shop',
                   'qoqa.shipping.fee',
                   ]
    _sync_date_field = 'qoqa_sync_date'

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the Odoo ID
        :param unwrap: No effect in the direct binding
        :return: a recordset or an empty recordset if the external_id is not
                 mapped
        :rtype: recordset
        """
        bindings = self.model.with_context(active_test=False).search(
            [(self._external_field, '=', str(external_id))]
        )
        if not bindings:
            return self.model.browse()
        bindings.ensure_one()
        return bindings

    def to_backend(self, binding_id, wrap=False):
        """ Give the external ID for an OpenERP ID

        Wrap is not applicable for this binder because the binded record
        is the same than the binding record.

        :param binding_id: Odoo record or id for which we want the external id
        :param wrap: no effect on direct bindings
        :return: external identifier of the record
        """
        record = self.model.browse()
        if isinstance(binding_id, models.BaseModel):
            binding_id.ensure_one()
            record = binding_id
            binding_id = binding_id.id
        if not record:
            record = self.model.browse(binding_id)
        assert record
        return getattr(record, self._external_field)

    def unwrap_binding(self, binding_id, browse=False):
        """ For a binding record, give the normal record.

        Example: when called with a ``qoqa.product.product`` id,
        it will return the corresponding ``product.product`` id.

        No effect on a direct binding, it returns the same record

        :param browse: when True, returns a browse_record instance
                       rather than an ID
        """
        if isinstance(binding_id, models.BaseModel):
            binding = binding_id
        else:
            binding = self.model.browse(binding_id)
        if browse:
            return binding
        return binding.id

    def unwrap_model(self):
        """ For a binding model, gives the name of the normal model.

        Example: when called on a binder for ``qoqa.product.product``,
        it will return ``product.product``.

        On a direct binder, it returns the current model.

        This binder assumes that the normal model lays in ``openerp_id`` since
        this is the field we use in the ``_inherits`` bindings.
        """
        return self.model._name


@qoqa
class QoQaInheritsBinder(QoQaBinder):
    """
    Bindings are done on the binding model.

    Binding models are models called ``qoqa.{normal_model}``,
    like ``qoqa.res.partner`` or ``qoqa.product.product``.
    They ``_inherits`` from the normal models and contains
    the QoQa ID, the ID of the QoQa Backend and the additional
    fields belonging to the QoQa instance.
    """
    _model_name = ['qoqa.product.template',
                   'qoqa.product.product',
                   'qoqa.product.attribute',
                   'qoqa.product.attribute.value',
                   'qoqa.res.partner',
                   'qoqa.address',
                   'qoqa.sale.order',
                   'qoqa.sale.order.line',
                   'qoqa.discount.accounting',
                   'qoqa.discount.accounting.line',
                   'qoqa.crm.claim',
                   'qoqa.crm.claim.medium',
                   ]
