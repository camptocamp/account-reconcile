# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Vincent Renaville
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
from openerp.osv import orm, fields, osv
from openerp.addons.base_status.base_stage import base_stage


class crm_claim(orm.Model):
    """
    Add partner_id to the follower automatically issue #39
     """
    _inherit = 'crm.claim'

    def create(self, cr, uid, vals, context=None):
        claim_id = super(crm_claim, self).create(
            cr, uid, vals, context=context)
        if vals.has_key('partner_id'):
            if vals['partner_id']:
                self.message_subscribe(cr, uid, [claim_id], [vals['partner_id']], context=None)
        return claim_id

    def write(self, cr, uid, ids, vals, context=None):
        ## Remove previous partner
        if vals.has_key('partner_id'):
            if vals['partner_id']:
                previous_claim_list = self.browse(cr,uid,ids,context=context)
                for previous_claim in previous_claim_list:
                    ## If the partner selected differ from the partner previously selected:
                    if previous_claim.partner_id.id != vals['partner_id']:
                        self.message_unsubscribe(cr, uid, [previous_claim.id], [previous_claim.partner_id.id], context=context)
                    ## We subcribe the sected partner to it
                    self.message_subscribe(cr, uid, [previous_claim.id], [vals['partner_id']], context=context)
        res = super(crm_claim, self).write(
            cr, uid, ids, vals, context=context)
        return res
