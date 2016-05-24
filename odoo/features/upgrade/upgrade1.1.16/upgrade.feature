# -*- coding: utf-8 -*-
@upgrade_from_1.1.15 @qoqa

Feature: upgrade to 1.1.16

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | specific_fct                     |
      | specific_report                  |
      | picking_dispatch_group           |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.16"
