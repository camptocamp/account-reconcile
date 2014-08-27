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
        if vals.has_key('user_id'):
            if vals['user_id']:
                # If a suer is selected we remove all previous selected partner
                fol_obj = self.pool.get('mail.followers')
                fol_ids = fol_obj.search(cr, uid, [('res_model', '=', self._name), ('res_id', '=', claim_id)])
                old = [fol.partner_id.id for fol in fol_obj.browse(cr, uid, fol_ids)]
                self.message_unsubscribe(cr, uid, [claim_id], old, context=context)
                #
                user_obj = self.pool.get('res.users')
                responsible = user_obj.browse(cr,uid,vals['user_id'])
                self.message_subscribe(cr, uid, [claim_id], [responsible.partner_id.id], context=context)
        if vals.has_key('partner_id'):
            if vals['partner_id']:
                self.message_subscribe(cr, uid, [claim_id], [vals['partner_id']], context=context)
        return claim_id

    def write(self, cr, uid, ids, vals, context=None):
        ## Remove previous partner
        if vals.has_key('partner_id'):
            if vals['partner_id']:
                previous_claim_list = self.browse(cr,uid,ids,context=context)
                for previous_claim in previous_claim_list:
                    ## If the partner selected differ from the partner previously selected:
                    if previous_claim.partner_id:
                        if previous_claim.partner_id.id != vals['partner_id']:
                            self.message_unsubscribe(cr, uid, [previous_claim.id], [previous_claim.partner_id.id], context=context)
                    ## We subcribe the sected partner to it
                    self.message_subscribe(cr, uid, [previous_claim.id], [vals['partner_id']], context=context)
        ## Make the same for tu Responsible (user_id):
        if vals.has_key('user_id'):
            if vals['user_id']:
                user_obj = self.pool.get('res.users')
                responsible = user_obj.browse(cr,uid,vals['user_id'])
                previous_claim_list = self.browse(cr,uid,ids,context=context)
                for previous_claim in previous_claim_list:
                    ## If the partner selected differ from the partner previously selected:
                    if previous_claim.user_id:
                        if previous_claim.user_id.id != vals['user_id']:
                            self.message_unsubscribe(cr, uid, [previous_claim.id], [previous_claim.user_id.partner_id.id], context=context)
                    ## We subcribe the sected partner to it
                    self.message_subscribe(cr, uid, [previous_claim.id], [responsible.partner_id.id], context=context)

        res = super(crm_claim, self).write(
            cr, uid, ids, vals, context=context)
        return res
