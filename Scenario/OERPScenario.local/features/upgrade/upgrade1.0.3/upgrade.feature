# -*- coding: utf-8 -*-
@upgrade_from_1.0.2 @qoqa

Feature: upgrade to 1.0.3

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                |
      | ecotax                              |
      | connector_qoqa                      |
    Then my modules should have been installed and models reloaded

  @ecotax
  Scenario: Activate the ecotax checkbox on the ecotax tax codes
    Given I execute the SQL commands
    """
    UPDATE account_tax_code SET ecotax = TRUE WHERE name LIKE '%TAR%';
    """

  Scenario: update application version
    Given I set the version of the instance to "1.0.3"
