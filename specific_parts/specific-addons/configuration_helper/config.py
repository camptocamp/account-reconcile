# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: David BEAL, Copyright 2014 Akretion
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
import re

from openerp.osv import orm, fields


class AbstractConfigSettings(orm.AbstractModel):
    _name = 'abstract.config.settings'
    _description = 'Abstract configuration settings'
    # prefix field name to differentiate fields in company with those in config
    _prefix = 'setting_'
    # this is the class name to import in your module
    # (it should be ResCompany or res_company, depends of your code)
    _companyObject = None

    def _filter_field(self, field_key):
        """Inherit in your module to define for which company field
        you don't want have a matching related field"""
        return True

    def __init__(self, pool, cr):
        super(AbstractConfigSettings, self).__init__(pool, cr)
        if self._companyObject:
            #print '    self._companyObject._columns.keys()', self._companyObject._columns.keys(), '\n\n'
            for field_key in self._companyObject._columns:
                #print 'field_key', field_key
                #allows to exclude some field
                if self._filter_field(field_key):
                    args = ('company_id', field_key)
                    kwargs = {
                        'string': self._companyObject._columns[field_key].string,
                        'help': self._companyObject._columns[field_key].help,
                        'type': self._companyObject._columns[field_key]._type,
                    }
                    #print '\n  __dict__:', self._companyObject._columns[field_key].__dict__, '\n  keys:', self._companyObject._columns[field_key].__dict__.keys()
                    if '_obj' in self._companyObject._columns[field_key].__dict__.keys():
                        kwargs['relation'] = \
                            self._companyObject._columns[field_key]._obj
                    if '_domain' in \
                            self._companyObject._columns[field_key].__dict__.keys():
                        kwargs['domain'] = \
                            self._companyObject._columns[field_key]._domain
                    field_key = re.sub('^' + self._prefix, '', field_key)
                    self._columns[field_key] = \
                        fields.related(*args, **kwargs)

    _columns = {
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

    def related_field_to_populate(self, cr, uid, field, context=None):
        """Field with prefix name as 'module_' allows to
        install module.
        'company_id' field is used to store values
        in the right companies"""
        if field != 'company_id' and field[:6] != 'module':
            return True
        return False

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        " update related fields "
        values = {}
        values['currency_id'] = False
        if not company_id:
            return {'value': values}
        company = self.pool['res.company'].browse(
            cr, uid, company_id, context=context)
        for field in self._columns:
            if self.related_field_to_populate(cr, uid, field, context=context):
                cpny_field = self._columns[field].arg[-1]
                if self._columns[field]._type == 'many2one':
                    values[field] = company[cpny_field]['id'] or False
                else:
                    values[field] = company[cpny_field]
        return {'value': values}

    def create(self, cr, uid, values, context=None):
        "code from Yannick Vaucher (Camptocamp) "
        id = super(AbstractConfigSettings, self).create(
            cr, uid, values, context=context)
        # Hack: to avoid some nasty bug, related fields are not written
        # upon record creation.  Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        return id
