# -*- coding: utf-8 -*-
@upgrade_from_1.1.14 @qoqa

Feature: upgrade to 1.1.15

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | connector_qoqa                   |
      | qoqa_offer                       |
      | specific_report                  |
      | specific_fct                     |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.15"
