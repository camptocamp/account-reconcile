# -*- coding: utf-8 -*-


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
    UPDATE sale_exception
    SET code = E'if order.qoqa_bind_ids and abs(order.amount_total_without_voucher - order.qoqa_bind_ids[0].qoqa_amount_total) >= 0.01:\n    failed = True'
    WHERE id = (
        SELECT res_id FROM ir_model_data
        WHERE model = 'sale.exception'
        AND module = 'connector_qoqa'
        AND name = 'excep_wrong_total_amount'
    )

    """)  # noqa

    cr.execute("""
    UPDATE sale_exception
    SET code = E'if order.qoqa_bind_ids and abs(order.amount_total_without_voucher - order.qoqa_bind_ids[0].qoqa_payment_amount) >= 0.01:\n    failed = True'
    WHERE id = (
        SELECT res_id FROM ir_model_data
        WHERE model = 'sale.exception'
        AND module = 'connector_qoqa'
        AND name = 'excep_wrong_paid_amount'
    )

    """)  # noqa
