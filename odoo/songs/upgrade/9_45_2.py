# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem
from anthem.lyrics.records import add_xmlid


@anthem.log
def fix_sav_qoqa_responsible_group(ctx):
    """ Fix sav_qoqa_responsible group """

    # 1.
    res_groups_65 = ctx.env.ref(
        '__export__.res_groups_65', raise_if_not_found=False)
    sav_qoqa_resposible = ctx.env.ref(
        'qoqa_claim.sav_qoqa_resposible', raise_if_not_found=False)
    if res_groups_65 and sav_qoqa_resposible:
        sav_qoqa_resposible.unlink()
        ctx.env['ir.model.data'].search([
            ('name', '=', 'sav_qoqa_resposible'),
            ('module', '=', 'qoqa_claim')
        ]).unlink()

    # 2.
    ctx.env.cr.execute("""
    UPDATE ir_model_data
    SET module = 'qoqa_claim',
        name = 'sav_qoqa_responsible'
    WHERE module = '__export__' AND name = 'res_groups_65'
    """)


@anthem.log
def create_stock_picking_type_stock_journal_6_if_not_exists(ctx):
    """ Create stock_picking_type_stock_journal_6 if it does not exist """

    picking_operation = ctx.env.ref(
        '__setup__.stock_picking_type_stock_journal_6',
        raise_if_not_found=False
    )

    if picking_operation:
        add_xmlid(
            ctx,
            picking_operation,
            'qoqa_base_data.picking_type_postpone_delivery',
            noupdate=True
        )

        add_xmlid(
            ctx,
            picking_operation.sequence_id,
            'qoqa_base_data.seq_picking_type_postpone',
            noupdate=True
        )


@anthem.log
def pre(ctx):
    """Pre 9.45.2"""
    fix_sav_qoqa_responsible_group(ctx)
    create_stock_picking_type_stock_journal_6_if_not_exists(ctx)
