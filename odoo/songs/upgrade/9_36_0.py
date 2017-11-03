# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.uninstaller import uninstall


@anthem.log
def update_crm_stage_sequences(ctx):
    """ Update stage sequences to add new stage in between """
    # those sequences have tag no update that's why we need
    # to update them manually
    ctx.env.ref('crm_claim.stage_claim2').sequence = 29
    ctx.env.ref('crm_claim.stage_claim3').sequence = 30


@anthem.log
def main(ctx):
    # we will uninstalled modules
    uninstall(ctx, ['password_security'])
    update_crm_stage_sequences(ctx)
