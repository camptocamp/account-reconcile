# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import test_company_binder
import test_import_metadata
import test_product_attribute_exporter
import test_import_partner
import test_import_offer
import test_import_product
import test_import_order
import test_import_voucher

fast_suite = [
]

checks = [
    test_company_binder,
    test_import_metadata,
    test_product_attribute_exporter,
    test_import_partner,
    test_import_offer,
    test_import_product,
    test_import_order,
    test_import_voucher,
]

