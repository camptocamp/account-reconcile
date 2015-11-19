# -*- coding: utf.9 -*-
@upgrade_from_1.3.8 @qoqa

Feature: upgrade to 1.3.9

  Scenario: backup DB
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

  Scenario: Validate all moves
    Given I need to validate all moves from "01-01-2014" to "12-31-2014" on company "QoQa Services SA"

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.9"
