# -*- coding: utf-8 -*-
@upgrade_from_1.1 @qoqa

Feature: upgrade to 1.2
  This upgrade needs 2 steps because connector_base_product is a new
  dependency and needs to be installed. If it is installed, if we
  continue to run the upgrade, we get an error with a rml report already
  existing, because it tries to load 2 times the wine_ch_report addon.
  So in the first step we fix the dependency and in the second one we
  proceed with the real upgrade. (update of connector in the first one
  is required too because its datamodel changed).
  The steps **must** be run in 2 calls to oerpscenario

  @step1
  Scenario: First step of the upgrade script for release 1.2 (this step fails, that's "normal")
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                     |
      | connector                |
      | connector_base_product   |

  # Manually run
  # bin/start_openerp --workers=0 -u base --stop-after-init

  @step2
  Scenario: Second step of the upgrade script for release 1.2
    Given I install the required modules with dependencies:
      | name                      |
      | stock_orderpoint_creator  |
    Given I execute the SQL commands
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
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.0"
