# -*- coding: utf-8 -*-
@upgrade_from_1.3.0 @qoqa

Feature: upgrade to 1.3.1

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | account_advanced_reconcile_ref_deep_search |
      | specific_fct                               |
    Then my modules should have been installed and models reloaded

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.1"
