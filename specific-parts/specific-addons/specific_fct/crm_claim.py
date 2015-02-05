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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class crm_case_section(orm.Model):
    """ Category of Case """
    _inherit = "crm.case.section"

    _columns = {
        'notify': fields.boolean(
            'Notify on change'),
    }


class crm_claim(orm.Model):
    """
    Add partner_id to the follower automatically issue #39
     """
    _inherit = 'crm.claim'

    def create(self, cr, uid, vals, context=None):
        claim_id = super(crm_claim, self).create(cr, uid, vals,
                                                 context=context)
        if vals.get('user_id'):
            # If a user is selected we remove all previous selected
            # partners
            fol_obj = self.pool.get('mail.followers')
            fol_ids = fol_obj.search(cr, uid,
                                     [('res_model', '=', self._name),
                                      ('res_id', '=', claim_id)],
                                     context=context)
            followers = fol_obj.browse(cr, uid, fol_ids, context=context)
            old = [fol.partner_id.id for fol in followers]
            self.message_unsubscribe(cr, uid, [claim_id], old, context=context)
            user_obj = self.pool.get('res.users')
            responsible = user_obj.browse(cr, uid, vals['user_id'],
                                          context=context)
            self.message_subscribe(cr, uid, [claim_id],
                                   [responsible.partner_id.id],
                                   context=context)
            if vals.get('section_id'):
                section_obj = self.pool.get('crm.case.section')
                section = section_obj.browse(cr, uid, vals['section_id'],
                                             context=context)
                if section.notify:
                    self.notify_user(cr, uid, claim_id,
                                     responsible.partner_id.id,
                                     context=context)
        if vals.get('partner_id'):
            self.message_subscribe(cr, uid, [claim_id], [vals['partner_id']],
                                   context=context)
        return claim_id

    def notify_user(self, cr, uid, claim_id, partner_id, context=None):

        claim = self.browse(cr, uid, claim_id, context=context)
        body = _('A new CRM claim (%s) has been assigned to you'
                 % (claim.name))
        subject = _('New CRM claim has been assigned to you')
        self.message_post(cr, uid, [claim.id],
                          body=body, subject=subject,
                          type='email',
                          subtype='mail.mt_comment', parent_id=False,
                          attachments=None, context=context,
                          partner_ids=[partner_id])

    def notify_claim_only_specific_user(self, cr, uid, claim_id,
                                        partner_id, context=None):
        ##
        claim = self.browse(cr, uid, claim_id, context=context)
        followers_ids = self._get_followers(cr, uid, [claim.id],
                                            name=None, arg=None,
                                            context=context)
        all_partner_ids = []
        if 'message_follower_ids' in followers_ids[claim.id]:
                all_partner_ids = \
                    followers_ids[claim.id]['message_follower_ids']
                self.message_unsubscribe(
                    cr, uid,
                    [claim.id],
                    all_partner_ids,
                    context=context)
        self.notify_user(cr, uid, claim_id, partner_id, context=context)
        if all_partner_ids:
            self.message_subscribe(cr, uid, [claim.id],
                                   all_partner_ids, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        # Remove previous partner
        if vals.get('partner_id'):
            previous_claim_list = self.browse(cr, uid, ids, context=context)
            for previous_claim in previous_claim_list:
                # If the partner selected differ from the partner
                # previously selected:
                if previous_claim.partner_id:
                    if previous_claim.partner_id.id != vals['partner_id']:
                        self.message_unsubscribe(
                            cr, uid, [previous_claim.id],
                            [previous_claim.partner_id.id], context=context)
                # We subcribe the sected partner to it
                self.message_subscribe(cr, uid, [previous_claim.id],
                                       [vals['partner_id']], context=context)
        # Make the same for the Responsible (user_id):
        responsible = False
        if vals.get('user_id'):
            user_obj = self.pool.get('res.users')
            responsible = user_obj.browse(cr, uid, vals['user_id'],
                                          context=context)
            previous_claim_list = self.browse(cr, uid, ids, context=context)
            for previous_claim in previous_claim_list:
                # If the partner selected differ from the partner
                # previously selected:
                if previous_claim.user_id:
                    if previous_claim.user_id.id != vals['user_id']:
                        self.message_unsubscribe(
                            cr, uid,
                            [previous_claim.id],
                            [previous_claim.user_id.partner_id.id],
                            context=context)

                # We subcribe the selected partner to it
                self.message_subscribe(cr, uid,
                                       [previous_claim.id],
                                       [responsible.partner_id.id],
                                       context=context)
        if vals.get('section_id'):
            section_obj = self.pool.get('crm.case.section')
            section = section_obj.browse(cr, uid, vals['section_id'],
                                         context=context)
        else:
            section = None
        previous_claim_list = self.browse(cr, uid, ids, context=context)
        for previous_claim in previous_claim_list:
            if section:
                current_section = section
            else:
                current_section = previous_claim.section_id
            if responsible:
                current_responsible = responsible
            else:
                current_responsible = previous_claim.user_id
            if current_section.notify:
                partner_id_notify = current_responsible.partner_id.id,
                self.notify_claim_only_specific_user(cr, uid,
                                                     previous_claim.id,
                                                     partner_id_notify,
                                                     context=context)

        res = super(crm_claim, self).write(
            cr, uid, ids, vals, context=context)
        return res
