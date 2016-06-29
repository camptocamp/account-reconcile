# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta

from openerp import models, fields
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # used in custom attributes
    brand = fields.Char(string='Brand',
                        related='product_brand_id.name',
                        readonly=True)

    # TODO: seems related to historical margin, see how to adapt as
    # _read_flat is gone
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
        return super(ProductTemplate, self)._read_flat(
            cr, uid, ids, fields, context=context, load=load)
