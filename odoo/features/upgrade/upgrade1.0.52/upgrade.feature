# -*- coding: utf-8 -*-
@upgrade_from_1.0.51 @qoqa

Feature: upgrade to 1.0.52

  Scenario: I update the module qoqa_offer for duppicate 
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.0.52"
