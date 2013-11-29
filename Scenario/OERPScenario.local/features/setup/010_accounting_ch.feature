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
@accounting @ch @setup

Feature: Configure the CH's accounting

  @banks
  Scenario Outline: Create the bank account for QoQa CH
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I need a "account.journal" with oid: <journal_oid>
    And having:
      | key                       | value                       |
      | name                      | <journal_name>              |
      | code                      | <journal_code>              |
      | type                      | bank                        |
      | company_id                | by oid: scenario.qoqa_ch    |
      | currency                  | <currency>                  |
      | default_debit_account_id  | by code: <acc_code>         |
      | default_credit_account_id | by code: <acc_code>         |
      | allow_date                | false                       |
    Given I need a "res.partner.bank" with oid: <bank_oid>
    And having:
      | key        | value                     |
      | journal_id | by oid: <journal_oid>     |
      | partner_id | by name: QoQa Services SA |
      | bank_name  | <bank_name>               |
      | company_id | by oid: scenario.qoqa_ch  |
      | street     | <street>                  |
      | zip        | <zip>                     |
      | city       | <city>                    |
      | country_id | by code: CH               |
      | state      | bank                      |
      | acc_number | <iban>                    |
      | bank_bic   | <bic>                     |
      | active     | True                      |

    Examples: Bank Accounts
      | journal_oid                              | journal_code | journal_name                       | currency                           | acc_code | bank_oid                               | bank_name              | street               | zip  | city  | iban                       | bic         |
      | scenario.journal_ch_service_client       | BNK11        | Compte Service-client Qgroup       | false                              | 10110    | scenario.bank_ch_service_client        | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH68 0900 0000 1078 0685 6 | POFICHBEXXX |
      | scenario.journal_ch_fournisseur_chf      | BNK16        | Compte Fournisseurs Qgroup         | false                              | 10160    | scenario.bank_ch_fournisseur_chf       | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH55 0900 0000 1225 8688 3 | POFICHBEXXX |
      | scenario.journal_ch_client_manuel        | BNK15        | Compte Client manuel Qgroup        | false                              | 10150    | scenario.bank_ch_client_manuel         | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH83 0900 0000 1283 1083 4 | POFICHBEXXX |
      | scenario.journal_ch_enc_debiteur         | BNK10        | Compte Encaissement débiteur Qgroup| false                              | 10100    | scenario.bank_ch_enc_debiteur          | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH71 0900 0000 1771 3231 4 | POFICHBEXXX |
      | scenario.journal_ch_fournisseur_eur      | BNK12        | Compte Fournisseur Qgroup en EUR   | by name: EUR and company_id: False | 10120    | scenario.bank_ch_fournisseur_eur       | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH19 0900 0000 9115 5371 5 | POFICHBEXXX |
      | scenario.journal_ch_fournisseur_usd      | BNK14        | Compte Fournisseur Qgroup en USD   | by name: USD and company_id: False | 10140    | scenario.bank_ch_fournisseur_usd       | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH56 0900 0000 9114 7215 1 | POFICHBEXXX |
      #| scenario.journal_ch_projet_geelee_ch     | BNK          | Compte Projet Geelee.ch            | false                              |          | scenario.bank_ch_projet_geelee_ch      | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH29 0900 0000 1223 3631 5 | POFICHBEXXX |
      | scenario.journal_ch_salaires             | BNK20        | Compte Paiement Salaires           | false                              | 10200    | scenario.bank_ch_salaires              | UBS SA                 |                      | 1800 | Vevey | CH51 0025 5255 7757 4801 V | UBSWCHZH80A |
      | scenario.journal_ch_epargne              | BNK21        | Compte épargne                     | false                              | 10210    | scenario.bank_ch_epargne               | UBS SA                 |                      | 1800 | Vevey | CH10 0025 5255 7757 48C3 Z | UBSWCHZH80A |
      | scenario.journal_ch_garantie_loyer       | GAR11        | Compte garantie loyer              | false                              | 14110    | scenario.bank_ch_garantie_loyer        | UBS SA                 |                      | 1800 | Vevey | CH06 0025 5255 7757 48MK U | UBSWCHZH80A |


  @journals
  Scenario Outline: Create an accounting journal for a Bank Journal
    Given I need a "account.journal" with oid: <oid>
    And having:
      | key                       | value                    |
      | name                      | <name>                   |
      | code                      | <code>                   |
      | type                      | bank                     |
      | company_id                | by oid: scenario.qoqa_ch |
      | default_debit_account_id  | by code: <account>       |
      | default_credit_account_id | by code: <account>       |
      | allow_date                | false                    |

    Examples: Bank Journals
      | oid                                           | name                      | code   | account |
      | scenario.journal_import_cb_postfinance        | Import CB Postfinance     | POSTF  |   11001 |
      | scenario.journal_import_visa_mastercard_ch    | Import Visa / Mastercard  | VISA   |   11011 |
      | scenario.journal_paypal_ch                    | Paypal                    | PAYPA  |   10300 |
      | scenario.journal_reglement_postfinance        | Reglement Postfinance     | RPOSTF |   11000 |
      | scenario.journal_reglement_visa_mastercard_ch | Reglement Visa Mastercard | RVISA  |   11010 |
      | scenario.journal_swissbilling                 | Swissbilling              | SWISS  |   11011 |

  @journals
  Scenario Outline: Create an accounting journal for a Bank Journal
    Given I need a "account.journal" with oid: scenario.journal_bon_achat_ch
    And having:
      | key                       | value                    |
      | name                      | Bon d'achat              |
      | code                      | BONS                     |
      | type                      | bank                     |
      | company_id                | by oid: scenario.qoqa_ch |
      | default_debit_account_id  | by code: 20400           |
      | default_credit_account_id | by code: 11030           |
      | allow_date                | false                    |

  @default_accounts
  Scenario Outline: AFTER IMPORT OF CUSTOM CoA, COMPLETE DEFAULT ACCOUNTS ON MAIN PARTNERS
    Given I set global property named "<name>" for model "<model>" and field "<name>" for company with ref "scenario.qoqa_ch"
    And the property is related to model "account.account" using column "code" and value "<account_code>"

    Examples: Defaults accouts for QoQa CH
      | name                                 | model            | account_code |
      | property_account_receivable          | res.partner      |        11030 |
      | property_account_payable             | res.partner      |        20000 |
      | property_account_expense_categ       | product.category |        42000 |
      | property_account_income_categ        | product.category |        32000 |
      | property_stock_valuation_account_id  | product.category |        10900 |
      | property_stock_account_input         | product.template |        10900 |
      | property_stock_account_output        | product.template |        10900 |

  @tax
  Scenario Outline: Configure the taxes to price include
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "account.tax" with description: <tax_code>
    And having:
         | key           | value     |
         | price_include | True      |

    Examples: currencies
         | tax_code |
         | 2.5%     |
         | 3.8%     |
         | 8.0%     |
         | 0% excl. |

  @historic_account_tax
  Scenario: I create the historic account taxes for CH (7.6%,3.6%,2.4%) in order to import the previous years
    Given I need a "account.tax" with oid: scenario.vat_76
    And having
         | key                  | value                                                           |
         | name                 | TVA due a 7.6% (TN)                                             |
         | price_include        | True                                                            |
         | description          | 7.6%                                                            |
         | amount               | 0.076                                                           |
         | type                 | percent                                                         |
         | python_compute       | result = round((price_unit * 0.076) / 0.05) * 0.05              |
         | python_compute_inv   | result = round((price_unit * ( 1 - (1 / 1.076))) / 0.05) * 0.05 |
         | base_sign            | 1.0                                                             |
         | tax_sign             | 1.0                                                             |
         | ref_base_sign        | -1.0                                                            |
         | ref_tax_sign         | -1.0                                                            |
         | account_collected_id | by code: 1170                                                   |
         | account_paid_id      | by code: 1170                                                   |
         | company_id           | by oid: scenario.qoqa_ch                                        |
         | type_tax_use         | sale                                                            |
         | active               | False                                                           |
    Given I need a "account.tax" with oid: scenario.vat_36
    And having
         | key                  | value                                                           |
         | name                 | TVA due a 3.6% (TN)                                             |
         | price_include        | True                                                            |
         | description          | 3.6%                                                            |
         | amount               | 0.036                                                           |
         | type                 | percent                                                         |
         | python_compute       | result = round((price_unit * 0.036) / 0.05) * 0.05              |
         | python_compute_inv   | result = round((price_unit * ( 1 - (1 / 1.036))) / 0.05) * 0.05 |
         | base_sign            | 1.0                                                             |
         | tax_sign             | 1.0                                                             |
         | ref_base_sign        | -1.0                                                            |
         | ref_tax_sign         | -1.0                                                            |
         | account_collected_id | by code: 1170                                                   |
         | account_paid_id      | by code: 1170                                                   |
         | company_id           | by oid: scenario.qoqa_ch                                        |
         | type_tax_use         | sale                                                            |
         | active               | False                                                           |
    Given I need a "account.tax" with oid: scenario.vat_24
    And having
         | key                  | value                                                           |
         | name                 | TVA due a 2.4% (TN)                                             |
         | price_include        | True                                                            |
         | description          | 2.4%                                                            |
         | amount               | 0.024                                                           |
         | type                 | percent                                                         |
         | python_compute       | result = round((price_unit * 0.024) / 0.05) * 0.05              |
         | python_compute_inv   | result = round((price_unit * ( 1 - (1 / 1.024))) / 0.05) * 0.05 |
         | base_sign            | 1.0                                                             |
         | tax_sign             | 1.0                                                             |
         | ref_base_sign        | -1.0                                                            |
         | ref_tax_sign         | -1.0                                                            |
         | account_collected_id | by code: 1170                                                   |
         | account_paid_id      | by code: 1170                                                   |
         | company_id           | by oid: scenario.qoqa_ch                                        |
         | type_tax_use         | sale                                                            |
         | active               | False                                                           |

  @currency_rate
  Scenario: I create the historic currency rates so we can import sales orders from 2005
    Given I need a "res.currency.rate" with oid: scenario.rate_chf_2005
    And having:
         | key         | value            |
         | name        | 2005-01-01       |
         | rate        | 1.0              |
         | currency_id | by oid: base.CHF |
