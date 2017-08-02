# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_write_offs(ctx):
    """ Remove write-offs created by an error in the mass_reconcile process """
    ctx.env.cr.execute("""
        SELECT move_id
        FROM account_move_line
        WHERE quantity IS NULL
        AND (credit > 0.99 OR debit > 0.99)
        AND account_id = 2546
        AND create_date > '2017-04-28';
    """)
    move_ids = [x[0] for x in ctx.env.cr.fetchall()]
    moves = ctx.env['account.move'].browse(move_ids)
    moves.unlink()


@anthem.log
def update_import_move_line_balance(ctx):
    """ Imported move lines don't have any balance ; this fixes the issue """
    ctx.env.cr.execute("""
        UPDATE account_move_line
        SET balance = debit - credit
        WHERE (credit > 0.0 OR debit > 0.0)
        AND balance = 0.0;
    """)


@anthem.log
def main(ctx):
    remove_write_offs(ctx)
    update_import_move_line_balance(ctx)
