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

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper
                                                  )
from ..unit.import_synchronizer import (DirectBatchImport,
                                        QoQaImportSynchronizer,
                                        AddCheckpoint,
                                        )
from ..backend import qoqa


@qoqa
class ShopBatchImport(DirectBatchImport):
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
        importer = self.get_connector_unit_for_model(ShopImport)
        importer.run(record_id['id'], record=record_id)


@qoqa
class ShopImport(QoQaImportSynchronizer):
    """ Import one QoQa Shop (and create a sale.shop via _inherits).

    A record can be given, so the batch import can import all
    the shops at the same time.
    """
    _model_name = 'qoqa.shop'

    def _create(self, data):
        openerp_binding_id = super(ShopImport, self)._create(data)
        checkpoint = self.get_connector_unit_for_model(AddCheckpoint)
        checkpoint.run(openerp_binding_id)
        return openerp_binding_id


@qoqa
class ShopImportMapper(ImportMapper):
    _model_name = 'qoqa.shop'

    direct = []
    # XXX maybe should we map: languages

    _name_to_xmlid = {
        'QoQa.ch': 'shop_qoqa_ch',
        'Qwine.ch': 'shop_qwine_ch',
        'Qsport.ch': 'shop_qsport_ch',
        'Qstyle.ch': 'shop_qstyle_ch',
        'QoQa.fr': 'shop_qoqa_fr',
        'Qwine.fr': 'shop_qwine_fr',
        'Qooking.ch': 'shop_qooking_ch',
    }

    @mapping
    @only_create
    def company(self, record):
        qoqa_company_id = record['company']['id']
        binder = self.get_binder_for_model('res.company')
        openerp_id = binder.to_openerp(qoqa_company_id)
        return {'company_id': openerp_id}

    @mapping
    def name(self, record):
        name = record['name']
        return {'name': name}

    @only_create
    @mapping
    def openerp_id(self, record):
        """ Default sale shops are created in `qoqa_base_date`.

        Link with the existing sale shops.

        """
        name = record['name']
        # if no corresponding xml id is found (shops added after go-live),
        # a new shop will be created
        if name in self._name_to_xmlid:
            sess = self.session
            data_obj = sess.pool['ir.model.data']
            module = 'qoqa_base_data'
            xmlid = self._name_to_xmlid[name]
            cr, uid = sess.cr, sess.uid
            __, res_id = data_obj.get_object_reference(cr, uid, module, xmlid)
            return {'openerp_id': res_id}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
