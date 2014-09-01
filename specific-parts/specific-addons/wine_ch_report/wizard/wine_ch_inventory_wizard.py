# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright Camptocamp SA 2013
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

from openerp.osv import fields, orm


class WineCHInventoryWizard(orm.TransientModel):
    """Will launch wine CH report and pass required args"""

    _name = "wine.ch.inventory.wizard"
    _description = "Wine CH Report"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company',
                                      required=True),
        'inventory_date': fields.date('Inventory date'),
        'location_ids': fields.many2many('stock.location',
                                         string='Filter on locations'),
        'attribute_set_id': fields.many2one('attribute.set',
                                            'Wine attribute set'),
    }

    def _get_attribute_set_id(self, cr, uid, context=None):
        """
        Search for the wine attribute set
        """
        attr_obj = self.pool.get('attribute.set')
        return attr_obj.search(cr, uid,
                               ['|',
                                ('name', 'ilike', 'wine'),
                                ('name', 'ilike', 'vin'),
                                ],
                               context=context)

    def _default_company(self, cr, uid, context=None):
        company_obj = self.pool.get('res.company')
        return company_obj._company_default_get(cr, uid,
                                                'account.invoice',
                                                context=context)

    _defaults = {
        'attribute_set_id': _get_attribute_set_id,
        'company_id': _default_company,
    }

    def print_inventory_report(self, cr, uid, ids, data, context=None):
        data['form'] = self.read(cr, uid, ids,
                                 ['inventory_date',
                                  'location_ids',
                                  'attribute_set_id'],
                                 context=context)[0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'wine.ch.inventory.webkit',
                'datas': data}

    def print_cscv_form_report(self, cr, uid, ids, data, context=None):
        data['form'] = self.read(cr, uid, ids,
                                 ['inventory_date',
                                  'location_ids',
                                  'attribute_set_id'],
                                 context=context)[0]
        return {'type': 'ir.actions.report.xml',
                'report_name': 'wine.ch.cscv_form.webkit',
                'datas': data}
