# -*- coding: utf-8 -*-
@upgrade_from_1.1.14 @qoqa

Feature: upgrade to 1.1.15

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | connector_qoqa                   |
      | web_warning_on_save              |
      | qoqa_offer                       |
      | purchase_order_webkit            |
      | specific_fct                     |
      | specific_report                  |
    Then my modules should have been installed and models reloaded

    Given I re-export to QoQa the product categories
    Given I set the version of the instance to "1.1.15"
