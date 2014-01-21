# -*- coding: utf-8 -*-
@upgrade_from_1.0.3 @qoqa

Feature: upgrade to 1.0.4

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                 |
      | connector_qoqa                       |
      | delivery_carrier_label_dispatch      |
      | delivery_carrier_label_postlogistics |
    Then my modules should have been installed and models reloaded

  Scenario: update application version
    Given I set the version of the instance to "1.0.4"
