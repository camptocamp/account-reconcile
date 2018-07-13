# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def fix_claim_on_mail_ir_model_data_noupdate(ctx):
    """ Fix claim_on_mail ir_model_data no """

    ctx.env.cr.execute("""
        UPDATE
          ir_model_data
        SET
          noupdate = false
        where
          module = 'crm_claim_mail' and
          name = 'stage_response_received'
    """)


@anthem.log
def pre(ctx):
    """Pre 9.46.0"""
    fix_claim_on_mail_ir_model_data_noupdate(ctx)
