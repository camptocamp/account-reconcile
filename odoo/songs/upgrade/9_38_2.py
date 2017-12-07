# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def disable_cron_automatic_workflow_ch(ctx):
    """Disable CH sale automatic workflow cron.

    Replaced by more fine-grained crons in
    sale_automatic_workflow_split
    """
    ctx.env.cr.execute("""
    UPDATE ir_cron
    SET active = false
    WHERE model = 'automatic.workflow.job'
    AND function = 'run';
    """)


@anthem.log
def pre(ctx):
    disable_cron_automatic_workflow_ch(ctx)
