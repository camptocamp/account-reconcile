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
@label  @setup

Feature: SHIPPING LABEL SETTING FOR QOQA
   As an administrator, I do the following installation steps.

  @shop_label_logo
  Scenario: I set a label logo on shops
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qoqa_ch
    And I set a postlogistics label logo from file "images/qoqa_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qwine_ch
    And I set a postlogistics label logo from file "images/qwine_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qsport_ch
    And I set a postlogistics label logo from file "images/qsport_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qstyle_ch
    And I set a postlogistics label logo from file "images/qstyle_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qooking_ch
    And I set a postlogistics label logo from file "images/qooking_label.png"

  @postlogistics_config
# Create an alias per alias in gmail to affect the right team
  Scenario: I configure postlogistics authentification
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | name                           | value                       |
      | postlogistics_username         | TU_9272_06                  |
      | postlogistics_password         | x1KsSvyY6X                  |
      | postlogistics_license_less_1kg | 60035471                    |
      | postlogistics_license_more_1kg | 60035471                    |
      | postlogistics_license_vinolog  | 60035471                    |
      | postlogistics_office           | 1030 Bussigny-près-Lausanne |
