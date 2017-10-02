# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def modify_password_parameters(ctx):
    """ Change password security parameters """
    ctx.env.cr.execute("""
        UPDATE res_company
        SET password_length = 8,
        password_expiration = 180,
        password_minimum = 0
        WHERE id = 3;
    """)


@anthem.log
def update_password_write_date(ctx):
    """ Update last write date for passwords """
    ctx.env.cr.execute("""
        UPDATE res_users
        SET password_write_date = current_timestamp;
    """)


@anthem.log
def add_twint_journal_xmlid(ctx):
    """ Change password security parameters """
    ctx.env['ir.model.data'].create({
        'module': 'scenario',
        'name': 'Import TWINT',
        'model': 'account.journal',
        'res_id': 86
    })


@anthem.log
def main(ctx):
    modify_password_parameters(ctx)
    update_password_write_date(ctx)
    add_twint_journal_xmlid(ctx)
