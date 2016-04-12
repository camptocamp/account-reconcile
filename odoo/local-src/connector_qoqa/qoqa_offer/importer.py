# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper)
from ..backend import qoqa
from ..unit.importer import QoQaImporter, DelayedBatchImporter
from ..unit.mapper import FromAttributes
from ..exception import QoQaError


@qoqa
class OfferBatchImport(DelayedBatchImporter):
    """ Import the QoQa offers.

    For every offer's id in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.offer'


@qoqa
class QoQaOfferImport(QoQaImporter):
    """ Import the description of the offer.

    All the offer's fields are master in OpenERP but the
    ``description`` field.
    This field is filed on the QoQa Backend and we get
    back its value on OpenERP.

    """
    _model_name = 'qoqa.offer'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        website_id = rec['data']['attributes']['website_id']
        self._import_dependency(website_id, 'qoqa.shop')

    def _import(self, binding_id):
        """ Use the user from the shop's company for the import

        Allowing the records rules to be applied.

        """
        shop_binder = self.binder_for('qoqa.shop')
        qoqa_shop_id = self.qoqa_record['data']['attributes']['website_id']
        shop_binding = shop_binder.to_openerp(qoqa_shop_id)
        shop_binding = self.env['qoqa.shop'].search([], limit=1)
        user = shop_binding.company_id.connector_user_id
        if not user:
            raise QoQaError('No connector user configured for company %s' %
                            shop_binding.company_id.name)
        with self.session.change_user(user.id):
            super(QoQaOfferImport, self)._import(binding_id)


@qoqa
class QoQaOfferImportMapper(ImportMapper, FromAttributes):
    _model_name = 'qoqa.offer'

    direct = []

    from_attributes = [
        ('name', 'name'),
    ]

    @mapping
    def shop(self, record):
        data = record.get('data', {})
        qoqa_website_id = data['attributes']['website_id']
        shop_binder = self.binder_for('qoqa.shop')
        binding = shop_binder.to_openerp(qoqa_website_id)
        assert binding, "shop %s should have been imported" % qoqa_website_id
        return {'qoqa_shop_id': binding.id}
