# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@holding_setup @setup

Feature: Configure the Holding company

@price_type_holding @price_type @pricelist
  Scenario Outline: CREATE PRICETYPE PER COMPANY
     Given I need a "product.price.type" with oid: <oid>
     And having:
      | key                       | value                    |
      | name                      | <name>                   |
      | currency_id               | by name: <currency>      |
      | company_id                | by oid: base.main_company |
      | field                     | <field>                  |

    Examples: Defaults price type for QoQa CH
      |oid                     | name                        | currency         | field          |
      | product.list_price     | Public Price CHF Holding    | CHF              | standard_price |
      | product.standard_price | Cost Price CHF Holding      | CHF              | list_price     |

  @pricelist_holding @pricelist
  Scenario: Pricelist for Holding
    Given I find a "product.pricelist" with oid: product.list0
    And having:
    | name                | value                             |
    | name                | Liste de prix publique Holding    |
    | company_id          | by oid: base.main_company         |
    | currency_id         | by oid: base.CHF                  |

    Given I find a "product.pricelist.item" with oid: purchase.item0
    And having:
    | name                | value                             |
    | name                | Liste de prix achat Holding       |
    And I set selection field "base" with name: Cost Price CHF Holding

    Given I find a "product.pricelist.item" with oid: product.item0
    And having:
    | name                | value                             |
    | name                | Liste de prix publique Holding       |
    And I set selection field "base" with name: Public Price CHF Holding

  @pricelist_property_holding @pricelist
  Scenario: Pricelist property for Holding
    Given I find a "ir.property" with oid: product.property_product_pricelist
    And having:
    | name                | value                             |
    | name                | property_product_pricelist_holding|
    | company_id          | by oid: base.main_company         |
    Given I find a "ir.property" with oid: purchase.property_product_pricelist_purchase
    And having:
    | name                | value                             |
    | name                | property_product_pricelist_purchase_holding|
    | company_id          | by oid: base.main_company         |
