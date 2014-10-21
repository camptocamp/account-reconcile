# -*- coding: utf-8 -*-
@upgrade_1.1.3 @qoqa

Feature: upgrade to 1.1.3

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | picking_dispatch                           |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE picking_dispatch
    SET company_id = res_users.company_id
    FROM res_users
    WHERE res_users.id = picker_id;
    """

    Given I set the version of the instance to "1.1.3"
