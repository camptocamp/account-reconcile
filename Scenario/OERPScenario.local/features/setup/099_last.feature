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
                     'ir_values_product_taxes_holding',
                     'ir_values_product_supplier_taxes_ch',
                     'ir_values_product_supplier_taxes_fr',
                     'ir_values_product_supplier_taxes_holding',
                     'ir_values_template_taxes_ch',
                     'ir_values_template_taxes_fr',
                     'ir_values_template_taxes_holding',
                     'ir_values_template_supplier_taxes_ch',
                     'ir_values_template_supplier_taxes_fr',
                     'ir_values_template_supplier_taxes_holding')
    )
    """

  @wine @filters
  Scenario: I create default filters for the wine move analysis
    Given I need an "ir.filters" with oid: scenario.filter_wine_form_b_ch
    And having:
      | key        | value                                                                                                          |
      | name       | Formulaire B en litres de vin CH                                                                               |
      | model_id   | report.wine.move.analysis                                                                                      |
      | domain     | [['attribute_set_id', '=', 2], ['location_id', '=', 12], ['location_dest_id', '=', 9], ['state', '=', 'done']] |
      | context    | {'default_attribute_set_id': 2, 'default_location_id': 12, 'default_location_dest_id': 9}                      |
      | user_id    | False                                                                                                          |
      | is_default | True                                                                                                           |
    Given I need an "ir.filters" with oid: scenario.filter_liquor_form_b_ch
    And having:
      | key      | value                                                                                                          |
      | name     | Formulaire B en litres de spiritueux CH                                                                        |
      | model_id | report.wine.move.analysis                                                                                      |
      | domain   | [['attribute_set_id', '=', 3], ['location_id', '=', 12], ['location_dest_id', '=', 9], ['state', '=', 'done']] |
      | context  | {'default_attribute_set_id': 3, 'default_location_id': 12, 'default_location_dest_id': 9}                      |
      | user_id  | False                                                                                                          |
    Given I need an "ir.filters" with oid: scenario.filter_wine_form_b_fr
    And having:
      | key      | value                                                                                                          |
      | name     | Formulaire B en litres de vin FR                                                                               |
      | model_id | report.wine.move.analysis                                                                                      |
      | domain   | [['attribute_set_id', '=', 2], ['location_id', '=', 18], ['location_dest_id', '=', 9], ['state', '=', 'done']] |
      | context  | {'default_attribute_set_id': 2, 'default_location_id': 18, 'default_location_dest_id': 9}                      |
      | user_id  | False                                                                                                          |
    Given I need an "ir.filters" with oid: scenario.filter_liquor_form_b_fr
    And having:
      | key      | value                                                                                                          |
      | name     | Formulaire B en litres de spiritueux FR                                                                        |
      | model_id | report.wine.move.analysis                                                                                      |
      | domain   | [['attribute_set_id', '=', 3], ['location_id', '=', 18], ['location_dest_id', '=', 9], ['state', '=', 'done']] |
      | context  | {'default_attribute_set_id': 3, 'default_location_id': 18, 'default_location_dest_id': 9}                      |
      | user_id  | False                                                                                                          |
