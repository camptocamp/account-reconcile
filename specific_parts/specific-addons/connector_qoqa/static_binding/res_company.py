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
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa
from ..exception import QoQaError


class res_company(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'qoqa_id': fields.char('ID on QoQa'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
        })
        return super(res_company, self).copy_data(
            cr, uid, id, default=default, context=context)


@qoqa
class CompanyBinder(QoQaDirectBinder):
    _model_name = ['res.company']

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        Raises a py:class:`~openerp.addons.connector_qoqa.exception.QoQaError`
        if no OpenERP ID is found.

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: No effect in the direct binding
        :return: ID of the record in OpenERP
        :rtype: int
        """
        openerp_id = super(CompanyBinder, self).to_openerp(external_id,
                                                           unwrap=unwrap)
        if openerp_id is None:
            raise QoQaError('No company found in OpenERP for the QoQa ID: %s' %
                            external_id)
        return openerp_id

    def to_backend(self, binding_id):
        """ Give the external ID for an OpenERP ID

        Raises a py:class:`~openerp.addons.connector_qoqa.exception.QoQaError`
        if no QoQa ID is found.

        :param binding_id: OpenERP ID for which we want the external id
        :return: backend identifier of the record
        """
        qoqa_id = super(CompanyBinder, self).to_backend(binding_id)
        if qoqa_id is None:
            raise QoQaError('The QoQa ID is not configured on the company '
                            'with ID: %s' % binding_id)
        return qoqa_id

    def bind(self, external_id, binding_id):
        """ Company are not synchronized, raise an error """
        raise TypeError('A company is not synchronized, thus, bind() '
                        'is not applicable')
