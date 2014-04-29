# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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
from itertools import chain
from openerp.osv import orm, fields


class crm_claim(orm.Model):
    _inherit = 'crm.claim'

    _columns = {
        # should always be readonly since it is used to match
        # incoming emails
        'number': fields.char(
            'Number', readonly=True,
            required=True,
            select=True,
            help="Company internal claim unique number"),
        # field used to keep track of the claims merged into this one,
        # so a the failsafe method that link emails from the number
        # can keep working based on the old numbers
        'merged_numbers': fields.serialized('Merged claims numbers'),
    }

    def _merge_data(self, cr, uid, merge_in, claims, fields, context=None):
        result = super(crm_claim, self)._merge_data(
            cr, uid, merge_in, claims, fields, context=context)
        numbers = merge_in.merged_numbers or []
        for claim in claims:
            numbers.append(claim.number)
            if claim.merged_numbers:
                numbers += claim.merged_numbers
        result['merged_numbers'] = numbers
        return result

    def _merge_fields(self, cr, uid, context=None):
        merge_fields = super(crm_claim, self)._merge_fields(
            cr, uid, context=context)
        if 'merged_numbers' in merge_fields:
            merge_fields.remove('merged_numbers')
        return merge_fields
