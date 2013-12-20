@upgrade_from_1.0.0

Feature: upgrade to 1.0.1

  Scenario: upgrade
    Given I back up the database to "~/instances/openerp_prod_qoqa/databases/"
    Given I install the required modules:
      | name                      |
      | connector_qoqa            |
    Then my modules should have been installed and models reloaded

    # Scenario: reconfigure sales
    #   Given I am configuring the company with ref "base.main_company"
    #   Given I need a "sale.config.settings" with oid: scen.sale_settings_doremi
    #    And having:
    #    | name                        | value   |
    #    | group_sale_delivery_address | true    |
    #    | group_discount_per_so_line  | true    |
    #    | group_multiple_shops        | true    |
    #    | group_invoice_deli_orders   | true    |
    #    | group_invoice_so_lines      | true    |
    #    | group_sale_pricelist        | true    |
    #    | default_order_policy        | picking |
    #    Then execute the setup

  Scenario: update application version
    Given I set the version of the instance to "1.0.1"
