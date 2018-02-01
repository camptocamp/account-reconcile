# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def enable_issuance_import_cron(ctx):
    """Enable the cron that import accounting issuances"""
    ctx.env.cr.execute("""
    UPDATE ir_cron
    SET active = true
    WHERE id = (
    SELECT res_id
    FROM ir_model_data
    WHERE module = 'connector_qoqa'
    AND name = 'ir_cron_qoqa_import_discount_accounting')
    """)


@anthem.log
def post(ctx):
    enable_issuance_import_cron(ctx)
