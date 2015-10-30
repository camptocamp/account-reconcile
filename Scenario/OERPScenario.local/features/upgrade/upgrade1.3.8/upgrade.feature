# -*- coding: utf-8 -*-
@upgrade_from_1.3.7 @qoqa

Feature: upgrade to 1.3.8

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

    Given I update the module list
    Given I install the required modules with dependencies:
      | name             |
      | specific_fct     |
    Then my modules should have been installed and models reloaded

  Scenario: change sequence from RMA- to SOS-
    Given I execute the SQL commands
    """
    UPDATE ir_sequence SET prefix = 'SOS-' WHERE code = 'crm.claim.rma' AND prefix = 'RMA-';
    """

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.8"
