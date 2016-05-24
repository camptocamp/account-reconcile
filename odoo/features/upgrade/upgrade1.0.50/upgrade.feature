# -*- coding: utf-8 -*-
@upgrade_from_1.0.49 @qoqa

Feature: upgrade to 1.0.50

  Scenario: I update the module qoqa_offer for duppicate 
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name           |
      | qoqa_offer |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.0.50"
