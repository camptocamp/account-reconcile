# -*- coding: utf-8 -*-
@upgrade_from_1.0.54 @qoqa

Feature: upgrade to 1.1.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | stock_picking_update_date                  |
    Then my modules should have been installed and models reloaded

    Given I find a "mass.object" with name: Bon de livraison
    And I add the field with oid stock_picking_update_date.field_stock_picking_date_expected_5267 to the mass editing

    Given I set the version of the instance to "1.1.0"
