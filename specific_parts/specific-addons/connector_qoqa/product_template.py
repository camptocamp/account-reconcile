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

from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  ExportMapper)
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            on_record_unlink,
                                            )
from . import consumer
from .backend import qoqa
from .unit.export_synchronizer import QoQaExporter
from .unit.delete_synchronizer import QoQaDeleteSynchronizer


class qoqa_product_template(orm.Model):
    _name = 'qoqa.product.template'
    _inherit = 'qoqa.binding'
    _inherits = {'product.template': 'openerp_id'}
    _description = 'QoQa Template'

    _columns = {
        'openerp_id': fields.many2one('product.template',
                                      string='Template',
                                      required=True,
                                      ondelete='restrict'),
        'created_at': fields.date('Created At (on QoQa)'),
        'updated_at': fields.date('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A product with the same ID on QoQa already exists")
    ]


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.product.template',
            'openerp_id',
            string='QoQa Bindings'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(product_product, self).copy_data(cr, uid, id,
                                                      default=default,
                                                      context=context)


@on_record_create(model_names='qoqa.product.template')
@on_record_write(model_names='qoqa.product.template')
def delay_export(session, model_name, record_id, fields=None):
    consumer.delay_export(session, model_name, record_id, fields=fields)


@on_record_write(model_names='product.template')
def delay_export_all_bindings(session, model_name, record_id, fields=None):
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, fields=fields)


@on_record_unlink(model_names='qoqa.product.template')
def delay_unlink(session, model_name, record_id):
    consumer.delay_unlink(session, model_name, record_id)


@qoqa
class TemplateDeleteSynchronizer(QoQaDeleteSynchronizer):
    """ Product deleter for QoQa """
    _model_name = ['qoqa.product.template']


@qoqa
class TemplateExporter(QoQaExporter):
    _model_name = ['qoqa.product.template']


@qoqa
class TemplateExportMapper(ExportMapper):
    _model_name = 'qoqa.product.template'

    direct = [('name', 'name'),
              ]

    @mapping
    def attributes(self, record):
        attrs = self.get_connector_unit_for_model(ProductAttribute)
        return attrs.get_values(record)
