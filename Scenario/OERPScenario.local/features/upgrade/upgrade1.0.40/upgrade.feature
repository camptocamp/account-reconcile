# -*- coding: utf-8 -*-
@upgrade_from_1.0.39 @qoqa

Feature: upgrade to 1.0.40

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                                   |
      | account_constraints                                    |
      | account_financial_report_webkit                        |
      | account_statement_cancel_line                          |
      | account_advanced_reconcile_bank_statement              |
      | account_move_line_search_extension                     |
    Then my modules should have been installed and models reloaded
    Given I execute the SQL commands
"""
    UPDATE account_bank_statement_line as sl 
    SET state = 'confirmed'
    FROM account_bank_statement as s 
    WHERE sl.statement_id = s.id 
    AND s.state = 'confirm';
"""
    Given I set the version of the instance to "1.0.40"
