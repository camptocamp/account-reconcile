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
@qoqa_ch @setup

Feature: Configure QoQa.ch

  @company_ch
  Scenario: Configure main partner and company
  Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
         | key        | value                      |
         | name       | QoQa Services SA           |
         | street     | Rue de l'Arc-en-Ciel 14    |
         | street2    |                            |
         | zip        | 1030                       |
         | city       | Bussigny-Lausanne          |
         | country_id | by code: CH                |
         | phone      | +41 21 633 20 80           |
         | fax        | +41 21 633 20 81           |
         | email      | contact@qoqa.ch            |
         | website    | http://www.qoqa.ch         |
         | vat        | CHE-105.616.108 TVA        |
         | parent_id  | by oid: base.main_company  |
         # temporary way of filling rml_header to change to position of header separator
         | rml_header | <header> <pageTemplate> <frame id="first" x1="1.3cm" y1="2.5cm" height="23.0cm" width="19.0cm"/> <pageGraphics> <!-- You Logo - Change X,Y,Width and Height --> <image x="1.3cm" y="27.6cm" height="40.0" >[[ company.logo or removeParentNode('image') ]]</image> <setFont name="DejaVu Sans" size="8"/> <fill color="black"/> <stroke color="black"/> <lines>1.3cm 27.5cm 20cm 27.5cm</lines> <drawRightString x="20cm" y="27.8cm">[[ company.rml_header1 ]]</drawRightString> <drawString x="1.3cm" y="27.2cm">[[ company.partner_id.name ]]</drawString> <drawString x="1.3cm" y="26.8cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]]</drawString> <drawString x="1.3cm" y="26.4cm">[[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]] - [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString> <drawString x="1.3cm" y="26.0cm">Phone:</drawString> <drawRightString x="7cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].phone or '' ]]</drawRightString> <drawString x="1.3cm" y="25.6cm">Mail:</drawString> <drawRightString x="7cm" y="25.6cm">[[ company.partner_id.address and company.partner_id.address[0].email or '' ]]</drawRightString> <lines>1.3cm 25.5cm 7cm 25.5cm</lines> <!--page bottom--> <lines>1.2cm 2.15cm 19.9cm 2.15cm</lines> <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString> <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString> <drawCentredString x="10.5cm" y="0.8cm">Contact : [[ user.name ]] - Page: <pageNumber/></drawCentredString> </pageGraphics> </pageTemplate> </header>   |
         | qoqa_id    | 1                          |

    Given the company has the "images/logo_qoqa_ch.png" logo
    And the company currency is "CHF" with a rate of "1.00"

  @webkit_logo_ch
  Scenario: configure logo
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And I have a header image "company_logo" from file "images/Logo-QoQa.jpg"

  @qoqa_ch_logistics
  Scenario: configure logistics
    Given I find a "stock.location" with oid: stock.stock_location_company
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |
    Given I find a "stock.location" with oid: stock.stock_location_output
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |
    Given I find a "stock.location" with oid: stock.stock_location_stock
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |
    Given I need a "stock.location" with oid: scenario.location_ch_sav
    And having:
    | name        | value                                |
    | name        | SAV                                  |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |
    Given I need a "stock.location" with oid: scenario.location_ch_non_reclame
    And having:
    | name        | value                                |
    | name        | Non réclamé                          |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |
    Given I need a "stock.location" with oid: scenario.location_ch_defectueux
    And having:
    | name        | value                                |
    | name        | Défectueux                           |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |
    Given I need a "stock.warehouse" with oid: stock.warehouse0
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |
    Given I find a "sale.shop" with oid: sale.sale_shop_1
    And having:
    | name         | value                    |
    | name         | QoQa Services SA         |
    | company_id   | by oid: scenario.qoqa_ch |
    | warehouse_id | by oid: stock.warehouse0 |
    Given I need a "stock.warehouse" with oid: scenario.warehouse_poste
    And having:
    | name          | value                                     |
    | name          | Poste Daillens                            |
    | lot_input_id  | by oid: stock.stock_location_stock  |
    | lot_output_id | by oid: stock.stock_location_output |
    | lot_stock_id  | by oid: stock.stock_location_stock  |
    | company_id    | by oid: scenario.qoqa_ch            |
    Given I need a "stock.warehouse" with oid: scenario.warehouse_gefco
    And having:
    | name          | value                                     |
    | name          | Gefco                                     |
    | lot_input_id  | by oid: stock.stock_location_stock  |
    | lot_output_id | by oid: stock.stock_location_output |
    | lot_stock_id  | by oid: stock.stock_location_stock  |
    | company_id    | by oid: scenario.qoqa_ch            |

  @account_chart_ch
  Scenario: Generate account chart for QoQa Services SA
    Given I have the module account installed
    And I want to generate account chart from chart template named "Plan comptable STERCHI" with "5" digits for company "QoQa Services SA"
    When I generate the chart
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And Create external ids for accounts from "setup/QoQa_ERP_Plan_comptable_v2_20131024_format_QoQa.csv"
    And "account.account" is imported from CSV "setup/QoQa_ERP_Plan_comptable_v2_20131024_format_QoQa.csv" using delimiter ";"
    And Delete accounts not listed by code in "setup/QoQa_ERP_Plan_comptable_v2_20131024_format_QoQa.csv"
    Then accounts should be available for company "QoQa Services SA"

  @fiscalyear_ch
    Scenario: create fiscal years
    Given I need a "account.fiscalyear" with oid: scenario.fy2013_ch
    And having:
    | name       | value                    |
    | name       | 2013                     |
    | code       | 2013                     |
    | date_start | 2013-01-01               |
    | date_stop  | 2013-12-31               |
    | company_id | by oid: scenario.qoqa_ch |
    And I create monthly periods on the fiscal year with reference "scenario.fy2013_ch"
    Then I find a "account.fiscalyear" with oid: scenario.fy2013_ch

  @pricelist_ch
    Scenario: Pricelist for QoQa.ch
    Given I find a "product.pricelist" with oid: product.list0
    And having:
    | name                | value                             |
    | company_id          | by oid: scenario.qoqa_ch          |
    | currency_id         | by oid: base.CHF                  |

  @pricetype_public
    Scenario: Pricetype should be set to CHF
    Given I find a "product.price.type" with oid: product.list_price
    And having:
    | name                | value                             |
    | currency_id         | by oid: base.CHF                  |

  @pricetype_cost
    Scenario: Pricetype should be set to CHF
    Given I find a "product.price.type" with oid: product.standard_price
    And having:
    | name                | value                             |
    | currency_id         | by oid: base.CHF                  |
