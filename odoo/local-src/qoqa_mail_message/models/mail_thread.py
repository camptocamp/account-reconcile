# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA (Nicolas Bessi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import types
from openerp.addons.mail.models.mail_thread import MailThread


# we need to monkey patch MailThread because inheriting
# MailThread is not applied on some models

def get_follower_partners(self):
    """Return the list of all partners that follow the current thread"""
    followers = self.message_partner_ids
    followers |= self.mapped('message_channel_ids.channel_partner_ids')
    return followers


def all_followers_are_users(self):
    """Predicate that return True
    if all the followers of the thread are Odoo users
    """
    followers = self.get_follower_partners()
    user_obj = self.env['res.users'].with_context(active_test=False)
    users_partners = user_obj.search([]).mapped('partner_id')
    return followers <= users_partners


MailThread.get_follower_partners = types.MethodType(
    get_follower_partners, None, MailThread)


MailThread.all_followers_are_users = types.MethodType(
    all_followers_are_users, None, MailThread)
