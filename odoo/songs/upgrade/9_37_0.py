# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem
<<<<<<< c775c3cab0d6b152f691ea6d31c5b10bebf97abf
=======

>>>>>>> PEP8


@anthem.log
def update_crm_stage_sequences(ctx):
    """ Update stage sequences to add new stage in between """
    # those sequences have tag no update that's why we need
    # to update them manually
    ctx.env.ref('crm_claim.stage_claim2').sequence = 29
    ctx.env.ref('crm_claim.stage_claim3').sequence = 30


@anthem.log
def recompute_qoqa_voucher_external_id(ctx):
    """Recompute new voucher composite external id"""
    for voucher in ctx.env['qoqa.voucher.payment'].search([]):
        if voucher.qoqa_order_id and voucher.qoqa_order_id.qoqa_id:
            new_qoqa_id = "{}__{}".format(voucher.qoqa_id,
                                          voucher.qoqa_order_id.qoqa_id)
            voucher.qoqa_id = new_qoqa_id


@anthem.log
def main(ctx):
    recompute_qoqa_voucher_external_id(ctx)
    update_crm_stage_sequences(ctx)
