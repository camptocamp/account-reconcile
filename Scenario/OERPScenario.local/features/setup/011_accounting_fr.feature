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
@accounting_fr @core_setup

Feature: Configure the FR's accounting

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

    Examples: Bank Journals (unused - for historic)
      | oid                                | name                            | code  |
      | scenario.journal_carte_bleue_old   | Carte Bleue Visa - plus utilisé | OLDCB |
      | scenario.journal_visa_fr_old       | Visa - plus utilisé             | OLDVI |
      | scenario.journal_mastercard_fr_old | Mastercard - plus utilisé       | OLDMS |
      | scenario.journal_sogenactif_old    | ? Sogenactif - plus utilisé     | OLDSO |
