# -*- coding: utf-8 -*-
@upgrade_from_1.1.7 @qoqa

Feature: upgrade to 1.1.8

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
    Then my modules should have been installed and models reloaded

    Given I re-import from QoQa the promo issuances with unbalanced lines

    Given I set the version of the instance to "1.1.8"
