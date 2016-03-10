# -*- coding: utf-8 -*-
@upgrade_to_1.8 @qoqa

Feature: upgrade to 1.8

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                      |
      | stock_picking_mass_assign |
      | specific_fct              |
    Then my modules should have been installed and models reloaded

  Scenario: add values to company
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | key                          | value                               |
      | unclaimed_stock_journal_id   | by name: Non-réclamé - renvoi colis |

  Scenario: delete claim lines with service products
    Given I execute the SQL commands
    """
    DELETE FROM claim_line
    WHERE product_id IN (
        SELECT id
        FROM product_product
        WHERE product_tmpl_id IN (
            SELECT id
            FROM product_template
            WHERE type NOT IN ('consu', 'product')
        )
    );
    """

  Scenario: upgrade application version
    Given I set the version of the instance to "1.8"
