# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa
from ..exception import QoQaError


class ResCompany(models.Model):
    _inherit = 'res.company'

    qoqa_id = fields.Char(string='ID on QoQa',
                          index=True,
                          copy=False)
    connector_user_id = fields.Many2one(comodel_name='res.users',
                                        string='Connector User',
                                        copy=False)

@qoqa
class CompanyBinder(QoQaDirectBinder):
    _model_name = ['res.company']

    def to_openerp(self, external_id, unwrap=False):
        # use super id to search the companies
        binding = super(CompanyBinder, self).to_openerp(external_id,
                                                        unwrap=unwrap)
        if not binding:
            raise QoQaError('No company found in Odoo for the QoQa ID: %s' %
                            external_id)
        return binding

    def to_backend(self, binding_id):
        qoqa_id = super(CompanyBinder, self).to_backend(binding_id)
        if not qoqa_id:
            raise QoQaError('The QoQa ID is not configured on the company '
                            'with ID: %s' % binding_id)
        return qoqa_id

    def bind(self, external_id, binding_id):
        """ Company are not synchronized, raise an error """
        raise TypeError('A company is not synchronized, thus, bind() '
                        'is not applicable')
