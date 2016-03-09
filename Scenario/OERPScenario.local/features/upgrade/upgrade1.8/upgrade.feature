# -*- coding: utf-8 -*-
@upgrade_to_1.8 @qoqa

Feature: upgrade to 1.8

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                      |
      | stock_picking_mass_assign |
      | specific_fct              |
    Then my modules should have been installed and models reloaded

  Scenario: upgrade application version
    Given I set the version of the instance to "1.8"
