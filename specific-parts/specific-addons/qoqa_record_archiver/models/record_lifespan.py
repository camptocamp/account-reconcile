# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
#

from openerp.osv import orm


class RecordLifespan(orm.Model):
    _inherit = 'record.lifespan'

    def _archive_domain(self, cr, uid, lifespan, expiration_date,
                        context=None):
        """ Returns the domain used to find the records to archive.

        Can be inherited to change the archived records for a model.
        """
        domain = super(RecordLifespan, self)._archive_domain(cr, uid, lifespan,
                                                             expiration_date,
                                                             context=context)
        model_name = lifespan.model
        if model_name == 'account.invoice':
            for idx, args in enumerate(domain):
                if len(args) == 3 and args[0] == 'state':
                    domain[idx] = ('state', 'in', ('paid', 'cancel'))
                if len(args) == 3 and args[0] == 'write_date':
                    new_args = ('date_invoice', '<', expiration_date)
                    domain[idx] = new_args
            return domain
        elif model_name == 'qoqa.offer':
            for idx, args in enumerate(domain):
                if len(args) == 3 and args[0] == 'state':
                    domain[idx] = ('date_end', '<', expiration_date)
                    break
            return domain
        elif model_name == 'sale.order':
            for idx, args in enumerate(domain):
                if len(args) == 3 and args[0] == 'write_date':
                    domain[idx] = ('date_order', '<', expiration_date)
                    break
            return domain
        elif model_name == 'crm.claim':
            for idx, args in enumerate(domain):
                if len(args) == 3 and args[0] == 'write_date':
                    domain[idx] = ('date', '<', expiration_date)
                    break
            return domain
        return domain
