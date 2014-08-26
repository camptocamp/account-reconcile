# -*- coding: utf-8 -*-
@upgrade_from_1.0.7 @qoqa

Feature: upgrade to 1.0.8

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | specific_fct                                           |
    Then my modules should have been installed and models reloaded

  @import @address
  Scenario: import again the addresses that have been modified on qoqa
    Given I import from QoQa the "qoqa.address" with QoQa ids from file "upgrade/1.0.8/1st_update.csv"
    And I import from QoQa the "qoqa.address" with QoQa ids from file "upgrade/1.0.8/2sd_update.csv"

  Scenario: update application version
    Given I set the version of the instance to "1.0.8"
