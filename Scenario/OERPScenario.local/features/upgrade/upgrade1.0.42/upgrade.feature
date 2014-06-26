# -*- coding: utf-8 -*-
@upgrade_from_1.0.41 @qoqa @Answer_to_the_Ultimate_Question_of_Life_the_Universe_and_Everything

Feature: upgrade to 1.0.42

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name           |
      | qoqa_offer     |
      | connector_qoqa |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.0.42"
