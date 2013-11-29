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
@users @setup

Feature: PRE-DEFINED USERS FOR TEST INSTANCE TO REPLACE BY USER FOR GO LIVE
   As an administrator, I do the following installation steps.

  @hide_useless_menu
  Scenario: GROUP TO HIDE USELESS MENU
    Given I need a "res.groups" with name: 'hidden menus' and oid: scenario._group
     And having:
        | name        | value                         |
        | name        | hidden menus                  |
        | category_id | by name: Accounting & Finance |

  Scenario Outline: Hide menu
     Given I need a "ir.ui.menu" with name: <name>
       And having:
        | name      | value               |
        | groups_id | by oid: scenario._group |

  Examples: Hide following menus
        | name                     |
        | Sale Receipts            |
        | Customer Payments        |
        | Purchase Receipts        |
        | Supplier Payments        |
        | Journal Vouchers         |
        | Automatic Reconciliation |
        | Multi-Currencies         |

  @user_erp_manager_ch
  Scenario: USERS SETTINGS
  Given I need a "res.users" with oid: scenario.user_ch
     And having:
     | name                     | value                              |
     | name                     | admin_ch                           |
     | login                    | admin_ch                           |
     | password                 | admin_ch                           |
     | lang                     | fr_FR                              |
     | company_id               | by oid: scenario.qoqa_ch           |
     | company_ids              | all by oid: scenario.qoqa_ch       |

    And we assign to user the groups below:
     | group_name                       |
#Sales
     | Sales / Manager                  |
#Purchase
     | Purchases / Manager               |
#Project
     | Project / Manager                |
#Warehouse
     | Warehouse / Manager              |
#Human_Resources
     | Employee                         |
#Sharing
     | Sharing / User                   |
#Administration
     | Access Rights                    |
#Connector
     | Connector / Connector Manager    |
#Technical_settings
     | Multi Currencies                 |
     | Advanced Attribute Option        |
     | Analytic Accounting              |
     | Sales Pricelists                 |
     | Purchase Pricelists              |
     | Costing Method                   |
     | Manage Multiple Units of Measure |
     | Manage Secondary Unit of Measure |
     | Manage Product Packaging         |
     | Manage Properties of Product     |
     | Analytic Accounting for Purchases|
     | Analytic Accounting for Sales    |
#Accounting_and_Finance
     | Accountant                       |
     | Invoicing & Payments             |
     | Financial Manager                |
     | Analytic Accounting              |
#Usability
     | Multi Companies                  |
     | Technical Features               |
#Other
     | Contact Creation                 |


  @user_erp_manager_fr
  Scenario: USERS SETTINGS
  Given I need a "res.users" with oid: scenario.user_fr
     And having:
     | name                     | value                              |
     | name                     | admin_fr                           |
     | login                    | admin_fr                           |
     | password                 | admin_fr                           |
     | lang                     | fr_FR                              |
     | company_id               | by oid: scenario.qoqa_fr           |
     | company_ids              | all by oid: scenario.qoqa_fr       |

    And we assign to user the groups below:
     | group_name                       |
#Sales
     | Sales / Manager                  |
#Purchase
     | Purchases / Manager               |
#Project
     | Project / Manager                |
#Warehouse
     | Warehouse / Manager              |
#Human_Resources
     | Employee                         |
#Sharing
     | Sharing / User                   |
#Administration
     | Access Rights                    |
#Connector
     | Connector / Connector Manager    |
#Technical_settings
     | Multi Currencies                 |
     | Advanced Attribute Option        |
     | Analytic Accounting              |
     | Sales Pricelists                 |
     | Purchase Pricelists              |
     | Costing Method                   |
     | Manage Multiple Units of Measure |
     | Manage Secondary Unit of Measure |
     | Manage Product Packaging         |
     | Manage Properties of Product     |
     | Analytic Accounting for Purchases|
     | Analytic Accounting for Sales    |
#Accounting_and_Finance
     | Accountant                       |
     | Invoicing & Payments             |
     | Financial Manager                |
     | Analytic Accounting              |
#Usability
     | Multi Companies                  |
     | Technical Features               |
#Other
     | Contact Creation                 |

  @setup_rules
  Scenario: DESACTIVATE SOME IR.RULE
    Given I find a possibly inactive "ir.rule" with oid: base.res_partner_rule
     And having:
        | name        | value                         |
        | active      | False                         |

  @companylinks
  Scenario: Links users to companies
    Given I find a "res.users" with oid: connector_qoqa.user_connector_ch
     And having:
        | name        | value                        |
        | company_id  | by oid: scenario.qoqa_ch     |
        | company_ids | all by oid: scenario.qoqa_ch |
        | lang        | fr_FR                        |

    Given I find a "res.users" with oid: connector_qoqa.user_connector_fr
     And having:
        | name        | value                        |
        | company_id  | by oid: scenario.qoqa_fr     |
        | company_ids | all by oid: scenario.qoqa_fr |
        | lang        | fr_FR                        |

  @user @connector
  Scenario: Assign groups for the connector users
    Given we select users below, even the deactivated ones:
    | login        |
    | connector_ch |
    | connector_fr |
    And we assign to users the groups below:
     | group_name                       |
#Sales
     | Sales / Manager                  |
#Purchase
     | Purchases / Manager               |
#Project
     | Project / Manager                |
#Warehouse
     | Warehouse / Manager              |
#Human_Resources
     | Employee                         |
#Sharing
     | Sharing / User                   |
#Administration
     | Access Rights                    |
#Connector
     | Connector / Connector Manager    |
#Technical_settings
     | Multi Currencies                 |
     | Advanced Attribute Option        |
     | Analytic Accounting              |
     | Sales Pricelists                 |
     | Purchase Pricelists              |
     | Costing Method                   |
     | Manage Multiple Units of Measure |
     | Manage Secondary Unit of Measure |
     | Manage Product Packaging         |
     | Manage Properties of Product     |
     | Analytic Accounting for Purchases|
     | Analytic Accounting for Sales    |
#Accounting_and_Finance
     | Accountant                       |
     | Invoicing & Payments             |
     | Financial Manager                |
     | Analytic Accounting              |
#Usability
     | Multi Companies                  |
     | Technical Features               |
#Other
     | Contact Creation                 |
