# -*- coding: utf-8 -*-
@upgrade_from_1.0.19 @qoqa

Feature: upgrade to 1.0.20

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | account_easy_reconcile                                 |
    Then my modules should have been installed and models reloaded

  @sql
  Scenario: I set the analytic accounts on the reconciliation methods
    Given I execute the SQL commands
    """
    UPDATE account_easy_reconcile_method SET analytic_account_id = 8 WHERE company_id = 3;
    UPDATE account_easy_reconcile_method SET analytic_account_id = 12 WHERE company_id = 4;
    """

  Scenario: update application version
    Given I set the version of the instance to "1.0.20"
