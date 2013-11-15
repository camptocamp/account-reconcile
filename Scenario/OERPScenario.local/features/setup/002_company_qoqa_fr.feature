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
@qoqa_fr @setup

Feature: Configure QoQa.fr

  @company_fr
  Scenario: Configure main partner and company for France
  Given I need a "res.company" with oid: scenario.qoqa_fr
    And having:
         | key               | value                                    |
         | name              | QoQa Services France                     |
         | street            | 20 rue Georges Barres                    |
         | street2           |                                          |
         | zip               | 33300                                    |
         | city              | Bordeaux                                 |
         | country_id        | by code: FR                              |
         | phone             | +33 5 56 37 57 08                        |
         | fax               | +33 5 56 37 57 08                        |
         | email             | clients@qoqa.fr                          |
         | website           | http://www.qoqa.fr                       |
         | parent_id         | by oid: base.main_company                |
         | vat               | FR80 504 886 607                         |
         | company_registry  | 504 886 607                              |
         | siret             | 504 886 607 00036                        |
         | ape               | 4791 A                                   |
         # temporary way of filling rml_header to change to position of header separator
         | rml_header        | <header> <pageTemplate> <frame id="first" x1="1.3cm" y1="2.5cm" height="23.0cm" width="19.0cm"/> <pageGraphics> <!-- You Logo - Change X,Y,Width and Height --> <image x="1.3cm" y="27.6cm" height="40.0" >[[ company.logo or removeParentNode('image') ]]</image> <setFont name="DejaVu Sans" size="8"/> <fill color="black"/> <stroke color="black"/> <lines>1.3cm 27.5cm 20cm 27.5cm</lines> <drawRightString x="20cm" y="27.8cm">[[ company.rml_header1 ]]</drawRightString> <drawString x="1.3cm" y="27.2cm">[[ company.partner_id.name ]]</drawString> <drawString x="1.3cm" y="26.8cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]]</drawString> <drawString x="1.3cm" y="26.4cm">[[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]] - [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString> <drawString x="1.3cm" y="26.0cm">Phone:</drawString> <drawRightString x="7cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].phone or '' ]]</drawRightString> <drawString x="1.3cm" y="25.6cm">Mail:</drawString> <drawRightString x="7cm" y="25.6cm">[[ company.partner_id.address and company.partner_id.address[0].email or '' ]]</drawRightString> <lines>1.3cm 25.5cm 7cm 25.5cm</lines> <!--page bottom--> <lines>1.2cm 2.15cm 19.9cm 2.15cm</lines> <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString> <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString> <drawCentredString x="10.5cm" y="0.8cm">Contact : [[ user.name ]] - Page: <pageNumber/></drawCentredString> </pageGraphics> </pageTemplate> </header>   |
         | qoqa_id           | 2                                        |
         | connector_user_id | by oid: connector_qoqa.user_connector_fr |

    Given the company has the "images/logo_qoqa_fr.png" logo
    And the company currency is "EUR" with a rate of "0.811035"

  @webkit_logo_fr
  Scenario: configure logo
    Given I am configuring the company with ref "scenario.qoqa_fr"
    And I have a header image "company_logo" from file "images/Logo-QoQa-fr.png"

  @qoqa_fr_logistics
  Scenario: configure logistics
    Given I need a "stock.location" with oid: scenario.stock_location_company_fr
    And having:
    | name        | value                       |
    | name        | QoQa Services France        |
    | usage       | view                        |
    | location_id | by name: Physical Locations |
    | company_id  | by oid: scenario.qoqa_fr    |
    Given I need a "stock.location" with oid: scenario.stock_location_output_fr
    And having:
    | name                  | value                                      |
    | name                  | Output                                     |
    | usage                 | internal                                   |
    | location_id           | by oid: scenario.stock_location_company_fr |
    | chained_location_id   | by name: Customers                         |
    | chained_location_type | customer                                   |
    | chained_auto_packing  | transparent                                |
    | chained_picking_type  | out                                        |
    | chained_journal_id    | by name: Delivery Orders                   |
    | company_id            | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.location" with oid: scenario.stock_location_stock_fr
    And having:
     | name        | value                                      |
     | name        | Stock                                      |
     | company_id  | by oid: scenario.qoqa_fr                   |
     | usage       | internal                                   |
     | location_id | by oid: scenario.stock_location_company_fr |
    Given I need a "stock.location" with oid: scenario.location_fr_sav
    And having:
    | name        | value                                      |
    | name        | SAV                                        |
    | location_id | by oid: scenario.stock_location_company_fr |
    | company_id  | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.location" with oid: scenario.location_fr_non_reclame
    And having:
    | name        | value                                      |
    | name        | Non réclamé                                |
    | location_id | by oid: scenario.stock_location_company_fr |
    | company_id  | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.location" with oid: scenario.location_fr_defectueux
    And having:
    | name        | value                                      |
    | name        | Défectueux                                 |
    | location_id | by oid: scenario.stock_location_company_fr |
    | company_id  | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.warehouse" with oid: scenario.warehouse_fr
    And having:
    | name          | value                                     |
    | name          | QoQa Services France                      |
    | lot_input_id  | by oid: scenario.stock_location_stock_fr  |
    | lot_output_id | by oid: scenario.stock_location_output_fr |
    | lot_stock_id  | by oid: scenario.stock_location_stock_fr  |
    | company_id    | by oid: scenario.qoqa_fr                  |
    Given I need a "sale.shop" with oid: sale.sale_shop_fr
    And having:
    | name         | value                         |
    | name         | QoQa Services France          |
    | company_id   | by oid: scenario.qoqa_fr      |
    | warehouse_id | by oid: scenario.warehouse_fr |

  @account_chart_fr
  Scenario: Generate account chart QoQa Services France
    Given I have the module account installed
    And I want to generate account chart from chart template named "Plan Comptable Général (France)" with "6" digits for company "QoQa Services France"
    When I generate the chart
    Given I am configuring the company with ref "scenario.qoqa_fr"
    And I fill the chart using "setup/PCG_QOQA_FRANCE.csv"
    Then accounts should be available for company "QoQa Services France"

  @fiscalyear_fr
    Scenario: create fiscal years
    Given I need a "account.fiscalyear" with oid: scenario.fy2013_fr
    And having:
    | name       | value                    |
    | name       | 2013                     |
    | code       | 2013                     |
    | date_start | 2013-01-01               |
    | date_stop  | 2013-12-31               |
    | company_id | by oid: scenario.qoqa_fr |
    And I create monthly periods on the fiscal year with reference "scenario.fy2013_fr"
    Then I find a "account.fiscalyear" with oid: scenario.fy2013_fr

  @pricelist_fr
    Scenario: Pricelist for QoQa.fr
    Given I need a "product.pricelist" with oid: scenario.pricelist_qoqa_fr
    And having:
    | name                | value                             |
    | name                | Liste de prix publique            |
    | type                | sale                              |
    | company_id          | by oid: scenario.qoqa_fr          |
    | currency_id         | by oid: base.EUR                  |

    Given I need a "product.pricelist.version" with oid: scenario.pricelist_version_qoqa_fr
    And having:
    | name         | value                                           |
    | name         | Version de la liste de Prix Publique par défaut |
    | pricelist_id | by oid: scenario.pricelist_qoqa_fr              |
    | company_id   | by oid: scenario.qoqa_fr                        |

    Given I need a "product.pricelist.item" with oid: scenario.pricelist_item_qoqa_fr
    And having:
    | name             | value                                      |
    | name             | Ligne de list de prix publique par défaut  |
    | price_version_id | by oid: scenario.pricelist_version_qoqa_fr |
    | company_id       | by oid: scenario.qoqa_fr                   |
     And I set selection field "base" with 1

  @sale_shop
    Scenario Outline: Configure sale shops
    Given I find a "sale.shop" with oid: <oid>
    And having:
    | name         | value                         |
    | warehouse_id | by oid: scenario.warehouse_fr |

    Examples: Shops
      | oid                            |
      | qoqa_base_data.shop_qoqa_fr    |
      | qoqa_base_data.shop_qwine_fr   |
