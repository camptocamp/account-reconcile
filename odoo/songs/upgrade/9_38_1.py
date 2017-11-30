# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def set_gift_payment_mode(ctx):
    """Flag 'Bon Cadeau' payment mode as with 'gift card' boolean"""
    ctx.env.cr.execute("""
    UPDATE account_payment_mode
    SET gift_card = true
    WHERE qoqa_id = '9';
    """)


@anthem.log
def pre(ctx):
    set_gift_payment_mode(ctx)
