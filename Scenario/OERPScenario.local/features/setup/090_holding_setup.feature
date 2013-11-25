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

  @pricelist_holding
  Scenario: Pricelist for Holding
    Given I find a "product.pricelist" with oid: product.list0
    And having:
    | name                | value                             |
    | company_id          | by oid: base.main_company         |
    | currency_id         | by oid: base.CHF                  |

   @pricelist_items_holding @pricelist_holding
    Given I find a "product.pricelist.item" with oid: purchase.item0
    And I set selection field "base" with -2


@price_type_holding @price_type
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
