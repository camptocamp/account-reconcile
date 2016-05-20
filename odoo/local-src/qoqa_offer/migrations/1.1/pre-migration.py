# -*- encoding: utf-8 -*-

__name__ = "move unit_price to lot_price "


def migrate(cr, version):
    if not version:
        return
    cr.execute("SELECT column_name "
               "FROM information_schema.columns "
               "WHERE table_name='qoqa_offer_position' "
               "AND column_name='lot_price';")
    if not cr.fetchone():
        cr.execute("ALTER TABLE qoqa_offer_position "
                   "RENAME COLUMN unit_price to lot_price ")
        cr.execute("ALTER TABLE qoqa_offer_position "
                   "ADD COLUMN unit_price numeric ")
        cr.execute("UPDATE qoqa_offer_position "
                   "SET unit_price = lot_price / lot_size ")
