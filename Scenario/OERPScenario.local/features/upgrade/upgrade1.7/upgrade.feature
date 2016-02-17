# -*- coding: utf-8 -*-
@upgrade_to_1.7 @qoqa

Feature: upgrade to 1.7

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                    |
    Then my modules should have been installed and models reloaded

  Scenario: upgrade application version
    Given I set the version of the instance to "1.7"
