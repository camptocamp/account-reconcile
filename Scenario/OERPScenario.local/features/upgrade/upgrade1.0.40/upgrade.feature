# -*- coding: utf-8 -*-
@upgrade_from_1.0.39 @qoqa

Feature: upgrade to 1.0.40

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                                   |
      | account_statement_cancel_line                          |
      | account_advanced_reconcile_bank_statement              |
      | account_move_line_search_extension                     |
      | account_move_validation_improvement                    |
    Then my modules should have been installed and models reloaded
    Given I set the version of the instance to "1.0.40"
