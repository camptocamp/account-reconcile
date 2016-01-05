# -*- coding: utf-8 -*-
@upgrade_to_1.5 @qoqa

Feature: upgrade to 1.5

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                 |
      | connector_qoqa       |
    Then my modules should have been installed and models reloaded

  Scenario: create "no job" delivery carrier
    Given I need a "delivery.carrier" with oid: scenario.carrier_nojob
    And having:
         | key        | value                                                |
         | name       | On-site delivery                                     |
         | partner_id | by oid: __export__.res_partner_8                     |
         | product_id | by oid: connector_ecommerce.product_product_shipping |
         | active     | True                                                 |
         | qoqa_type  | service                                              |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.5"
