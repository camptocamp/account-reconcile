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

from datetime import datetime, timedelta

from openerp.osv import orm, fields
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        # used in custom attributes
        'brand': fields.char('Brand', translate=True),
    }

    def _read_flat(self, cr, uid, ids, fields,
                   context=None, load='_classic_read'):
        if context is None:
            context = {}
        if (context.get('date_begin') is not None and
                context.get('time_begin') is not None):
            context = context.copy()
            date_fmt = DEFAULT_SERVER_DATE_FORMAT
            datetime_fmt = DEFAULT_SERVER_DATETIME_FORMAT
            begin = datetime.strptime(context.pop('date_begin'), date_fmt)
            begin += timedelta(hours=context.pop('time_begin'))
            context['to_date'] = begin.strftime(datetime_fmt)
        return super(product_template, self)._read_flat(
            cr, uid, ids, fields, context=context, load=load)
