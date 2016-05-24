# -*- encoding: utf-8 -*-

__name__ = "The quantities are now units and not lots"


def migrate(cr, version):
    if not version:
        return
    cr.execute("UPDATE qoqa_offer_position_variant v "
               "SET quantity = quantity * p.lot_size, "
               "    stock_sold = stock_sold * p.lot_size, "
               "    stock_residual = stock_residual * p.lot_size "
               "FROM qoqa_offer_position p "
               "WHERE p.id = v.position_id ")
