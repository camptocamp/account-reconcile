# -*- coding: utf-8 -*-
@upgrade_1.1.4 @qoqa

Feature: upgrade to 1.1.4

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | qoqa_offer                                 |
      | connector_qoqa                             |
      | web_environment                            |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE qoqa_backend
    SET import_product_product_from_date = '2014-10-01 00:00:00'
    WHERE id = 1
    """

    Given I set the version of the instance to "1.1.4"
