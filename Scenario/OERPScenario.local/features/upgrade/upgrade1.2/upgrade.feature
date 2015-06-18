# -*- coding: utf-8 -*-
@upgrade_from_1.1 @qoqa

Feature: upgrade to 1.2

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.0"
