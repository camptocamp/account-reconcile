# -*- coding: utf-8 -*-
@upgrade_1.1.6 @qoqa

Feature: upgrade to 1.1.6

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | qoqa_offer                                 |
      | specific_fct                               |
      | account_easy_reconcile                     |
      | account_financial_report_webkit            |
      | account_statement_account_partner_import   |
    Then my modules should have been installed and models reloaded

  Scenario: DB clean table account_move_line
    Given I execute the SQL commands
    """
    VACUUM FULL account_move_line;
    """

    Given I set the version of the instance to "1.1.6"
