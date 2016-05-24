# -*- coding: utf-8 -*-
@upgrade_from_1.0.36 @qoqa

Feature: upgrade to 1.0.37

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                                   |
      | account_advanced_reconcile_bank_statement              |
    Then my modules should have been installed and models reloaded
    Given I set the version of the instance to "1.0.37"
