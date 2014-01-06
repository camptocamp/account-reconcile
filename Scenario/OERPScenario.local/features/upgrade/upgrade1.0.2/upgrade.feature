# -*- coding: utf-8 -*-
@upgrade_from_1.0.1 @qoqa

Feature: upgrade to 1.0.2

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                 |
      | qoqa_offer                           |
    Then my modules should have been installed and models reloaded

  @cost_price
  Scenario: The cost prices have been imported on the holding, set them on the CH
    Given I execute the SQL commands
    """
    UPDATE product_price_history SET company_id = 3 WHERE company_id = 1;
    """

  Scenario: update application version
    Given I set the version of the instance to "1.0.2"
