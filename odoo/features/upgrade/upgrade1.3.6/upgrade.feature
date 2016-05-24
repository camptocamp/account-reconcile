# -*- coding: utf-8 -*-
@upgrade_from_1.3.5 @qoqa

Feature: upgrade to 1.3.6

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

    Given I update the module list
    Given I install the required modules with dependencies:
      | name             |
      | picking_dispatch |
    Then my modules should have been installed and models reloaded

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.6"
