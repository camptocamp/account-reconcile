# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@last  @setup

Feature: Configure things which must be done after all the other things... update or fix values

  @product @taxes
  Scenario: fix product taxes
    Given I set the taxes on all products

  @product @taxes @default
  Scenario: I set the default values for the taxes on the products
    Given I load the data file "setup/ir.values.yml"
    # OpenERP sets a value by default a key which prevent the default
    # value to be applied! It absolutely needs a NULL, which we can't
    # set with the ORM...
    And I execute the SQL commands
    """
    UPDATE ir_values SET key2 = NULL WHERE id IN (
        SELECT res_id FROM ir_model_data
        WHERE module = 'scenario'
        AND name IN ('ir_values_product_taxes_ch',
                     'ir_values_product_taxes_fr',
                     'ir_values_product_supplier_taxes_ch',
                     'ir_values_product_supplier_taxes_fr')
    )
    """
