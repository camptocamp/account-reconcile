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
@accounting @fr @setup

Feature: Configure the FR's accounting

  @banks
  Scenario Outline: Create the bank account for QoQa France
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I need a "account.journal" with oid: <journal_oid>
    And having:
      | key                       | value                       |
      | name                      | <journal_name>              |
      | code                      | <journal_code>              |
      | type                      | bank                        |
      | company_id                | by oid: scenario.qoqa_fr    |
      | currency                  | <currency>                  |
      | default_debit_account_id  | by code: <acc_code>         |
      | default_credit_account_id | by code: <acc_code>         |
      | allow_date                | false                       |
    Given I need a "res.partner.bank" with oid: <bank_oid>
    And having:
      | key            | value                         |
      | journal_id     | by oid: <journal_oid>         |
      | partner_id     | by name: QoQa Services France |
      | bank_name      | <bank_name>                   |
      | company_id     | by oid: scenario.qoqa_fr      |
      | street         | <street>                      |
      | zip            | <zip>                         |
      | city           | <city>                        |
      | country_id     | by code: FR                   |
      | state          | rib                           |
      | bank_code      | <bank_code>                   |
      | office         | <office>                      |
      | rib_acc_number | <rib_acc_number>              |
      | acc_number     | <iban>                        |
      | bank_bic       | <bic>                         |
      | key            | <key>                         |
      | active         | True                          |

    Examples: Bank Accounts
      | journal_oid         | journal_code | journal_name           | currency | acc_code | bank_oid         | bank_name   | street               | zip   | city     | bank_code | office | rib_acc_number | key | iban                              | bic         |
      | scenario.journal_fr | BNP4171      | Compte Bancaire France | false    | 512300   | scenario.bank_fr | BNP Paribas | 95 cours de la Marne | 33300 | Bordeaux | 30004     | 00340  | 00010116041    | 71  | FR67 3000 4003 4000 0101 1604 171 | BNPAFRPPBOR |


  @journals
  Scenario Outline: Create an accounting journal for a Bank Journal
    Given I need a "account.journal" with oid: <oid>
    And having:
      | key                       | value                    |
      | name                      | <name>                   |
      | code                      | <code>                   |
      | type                      | bank                     |
      | company_id                | by oid: scenario.qoqa_fr |
      | default_debit_account_id  | by code: 512102          |
      | default_credit_account_id | by code: 512102          |
      | allow_date                | false                    |

    Examples: Bank Journals
      | oid                            | name             | code  |
      | scenario.journal_carte_bleue   | Carte Bleue Visa | CBVIS |
      | scenario.journal_visa_fr       | Visa             | VISA  |
      | scenario.journal_mastercard_fr | Mastercard       | MASTR |
      | scenario.journal_paiement_3x   | Paiement 3x      | PAY3X |
      | scenario.journal_paypal_fr     | Paypal           | PAYPA |

  @currency_rate
  Scenario Outline: I create the historic currency rates so we can import sales orders from 2005
    Given I need a "res.currency.rate" with oid: scenario.rate_euro_<year>
    And having:
         | key         | value            |
         | name        | <year>-01-01     |
         | rate        | <rate>           |
         | currency_id | by oid: base.EUR |

   Examples: rates
      | year | rate   |
      | 2005 | 0.6469 |
      | 2006 | 0.6431 |
      | 2007 | 0.6244 |
      | 2008 | 0.6043 |
      | 2009 | 0.6684 |
      | 2010 | 0.6739 |
      | 2011 | 0.8017 |
      | 2012 | 0.8221 |
