# -*- coding: utf-8 -*-
@upgrade_from_1.0.34 @qoqa

Feature: upgrade to 1.0.35

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | specific_fct                                           |
      | account_easy_reconcile                                 |
      # update addons with updated xml
      | base                                                   |
    Then my modules should have been installed and models reloaded
    Given I set the version of the instance to "1.0.35"
