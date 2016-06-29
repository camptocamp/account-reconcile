# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


def pre_init_hook(cr):
    # as we change default_code to be mandatory, fill
    # something in the default_code
    cr.execute("""
    UPDATE product_product
    SET default_code = 'MIGR-' || id::varchar
    WHERE default_code IS NULL
    """)
