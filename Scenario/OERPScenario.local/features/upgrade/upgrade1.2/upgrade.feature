# -*- coding: utf-8 -*-
@upgrade_from_1.1 @qoqa

Feature: upgrade to 1.2

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    # Update module first
    Given I install the required modules with dependencies:
      | name                     |
      | stock_orderpoint_creator |
      | connector_base_product   |
  Scenario: Clean old stuf from renamed module stock_orderpoint_creator
    Given  I execute the SQL commands
    """
    DELETE FROM ir_model_constraint
      WHERE name IN (
        'order_point_creator_rel_stock_warehouse_orderpoint_template_id_fkey',
        'order_point_creator_rel_stock_warehouse_orderpoint_creator_id_fkey'
        )
    """
    Given I uninstall the following modules:
      | name                     |
      | stock_orderpoint_creator |
    Given I install the required modules with dependencies:
      | name                             |
      | base                             |
      | specific_fct                     |
      | connector                        |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.0"
