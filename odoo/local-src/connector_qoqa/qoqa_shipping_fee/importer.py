# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.unit.mapper import ImportMapper
from ..backend import qoqa
from ..unit.importer import QoQaImporter, BatchImporter
from ..unit.mapper import FromDataAttributes


@qoqa
class ShippingFeeBatchImporter(BatchImporter):
    """ Import the QoQa offers.

    For every offer's id in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.shipping.fee'


@qoqa
class ShippingFeeImportMapper(ImportMapper, FromDataAttributes):
    _model_name = 'qoqa.shipping.fee'

    from_data_attributes = [
        ('name', 'name'),
    ]


@qoqa
class ShippingFeeImporter(QoQaImporter):
    """ Import a shipping fee """
    _model_name = 'qoqa.shipping.fee'
