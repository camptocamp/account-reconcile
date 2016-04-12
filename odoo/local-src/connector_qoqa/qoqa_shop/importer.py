# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper
                                                  )
from ..unit.importer import DirectBatchImporter, QoQaImporter
from ..unit.mapper import FromAttributes
from ..backend import qoqa


@qoqa
class ShopBatchImporter(DirectBatchImporter):
    """ Import the records directly, without delaying the jobs.

    Import the QoQa Shops

    They are imported directly because this is a rare and fast operation,
    and we don't really bother if it blocks the UI during this time.
    """
    _model_name = 'qoqa.shop'

    def _import_record(self, record_id):
        """ Import the record directly.

        For the shops, the import does only 1 call to the
        API, it returns the data from all the shops.
        """
        importer = self.unit_for(ShopImporter)
        importer.run(record_id['id'], record=record_id)


@qoqa
class ShopImporter(QoQaImporter, FromAttributes):
    """ Import one QoQa Shop (and create a sale.shop via _inherits).

    A record can be given, so the batch import can import all
    the shops at the same time.
    """
    _model_name = 'qoqa.shop'


@qoqa
class ShopImportMapper(ImportMapper):
    _model_name = 'qoqa.shop'

    @mapping
    def attrs(self, record):
        return {
            'name': record['attributes']['name'],
            'identifier': record['attributes']['identifier'],
            'domain': record['attributes']['domain'],
        }

    @mapping
    @only_create
    def company(self, record):
        relationships = record['relationships']
        qoqa_company_id = relationships['company']['data']['id']
        binder = self.binder_for('res.company')
        binding = binder.to_openerp(qoqa_company_id)
        return {'company_id': binding.id}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
