# -*- coding: utf-8 -*-
@upgrade_to_1.9 @qoqa

Feature: upgrade to 1.9

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name            |
      | connector_qoqa  |
      | specific_fct    |
      | specific_report |
    Then my modules should have been installed and models reloaded

  Scenario: add values to company
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | key                | value          |
      | voucher_account_id | by code: 11044 |

  Scenario: update purchase pricelist items with "Cost Price CHF"
    Given I execute the SQL commands
    """
       UPDATE product_pricelist_item
       SET base = 4
       WHERE base = -2
       AND price_version_id IN (4, 8, 14);
    """

  Scenario: add new warehouse
    Given I need a "stock.warehouse" with oid: scenario.warehouse_poste2
    And having:
    | name          | value                               |
    | name          | Poste Dintikon                      |
    | lot_input_id  | by oid: stock.stock_location_stock  |
    | lot_output_id | by oid: stock.stock_location_output |
    | lot_stock_id  | by oid: stock.stock_location_stock  |
    | company_id    | by oid: scenario.qoqa_ch            |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.9"
