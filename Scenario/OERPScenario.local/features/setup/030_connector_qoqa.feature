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
@connector_qoqa @setup

Feature: Configure the connector's backend

  @qoqa_backend
  Scenario: Configure the QoQa backend
  Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    And having:
         | key             | value                        |
         | url             | http://admin.test02.qoqa.com |
         | default_lang_id | by code: fr_FR               |

  @automatic_workflows
  Scenario: Configure Sales Automatic Workflows
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.automatic_validation
    And having:
      | key                        | value           |
      | picking_policy             | one             |
      | invoice_quantity           | procurement     |
      | order_policy               | manual          |
      | validate_order             | True            |
      | validate_invoice           | True            |
      | create_invoice_on          | on_picking_done |
      | invoice_date_is_order_date | True            |
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.manual_validation
    And having:
      | key              | value       |
      | picking_policy   | one         |
      | invoice_quantity | procurement |
      | order_policy     | picking     |
      | validate_order   | False       |
      | validate_invoice | True        |

  @sale_payment_methods_ch
  Scenario Outline: Create the automatic payment methods for CH
  Given I need a "payment.method" with oid: <oid>
    And having:
      | key                 | value                                                |
      | name                | <name> (CH)                                          |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | <journal_id>                                         |

    Examples: Payment Methods
      | oid                                   | name                                | journal_id                             |
      | scenario.payment_method_postfinance   | Postfinance                         | by oid: scenario.journal_postfinance   |
      | scenario.payment_method_visa_ch       | Visa                                | by oid: scenario.journal_visa_ch       |
      | scenario.payment_method_mastercard_ch | Mastercard                          | by oid: scenario.journal_mastercard_ch |
      | scenario.payment_method_paypal_ch     | Paypal                              | by oid: scenario.journal_paypal_ch     |
      | scenario.payment_method_swissbilling  | Swissbilling (paiement par facture) | by oid: scenario.journal_swissbilling  |

    Examples: Payment Methods (unused now but kept for the history)
      | oid                                        | name                       | journal_id                                 |
      | scenario.payment_method_swikey_ch_old      | Swikey - plus utilisé      | by oid: scenario.journal_swikey_old        |
      | scenario.payment_method_postfinance_ch_old | Postfinance - plus utilisé | by oid: scenario.journal_postfinance_old   |
      | scenario.payment_method_mastercard_ch_old  | Mastercard - plus utilisé  | by oid: scenario.journal_mastercard_ch_old |
      | scenario.payment_method_visa_ch_old        | Visa - plus utilisé        | by oid: scenario.journal_visa_ch_old       |

  @sale_payment_methods_fr
  Scenario Outline: Create the automatic payment methods for FR
  Given I need a "payment.method" with oid: <oid>
    And having:
      | key                 | value                                                |
      | name                | <name> (FR)                                          |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | <journal_id>                                         |

    Examples: Payment Methods
      | oid                                    | name             | journal_id                             |
      | scenario.payment_method_carte_bleue    | Carte Bleue Visa | by oid: scenario.journal_carte_bleue   |
      | scenario.payment_method_visa_fr        | Visa             | by oid: scenario.journal_visa_fr       |
      | scenario.payment_method_mastercard_fr  | Mastercard       | by oid: scenario.journal_mastercard_fr |
      | scenario.payment_method_paiement_3x_fr | Paiement 3x      | by oid: scenario.journal_paiement_3x   |
      | scenario.payment_method_paypal_fr      | Paypal           | by oid: scenario.journal_paypal_fr     |

    Examples: Payment Methods (unused now but kept for the history)
      | oid                                        | name                             | journal_id                                 |
      | scenario.payment_method_carte_bleue_fr_old | Carte Bleue Visa  - plus utilisé | by oid: scenario.journal_carte_bleue_old   |
      | scenario.payment_method_visa_fr_old        | Visa  - plus utilisé             | by oid: scenario.journal_visa_fr_old       |
      | scenario.payment_method_mastercard_fr_old  | Mastercard  - plus utilisé       | by oid: scenario.journal_mastercard_fr_old |
      | scenario.payment_method_sogenactif_fr_old  | ? Sogenactif  - plus utilisé     | by oid: scenario.journal_sogenactif_old    |

  @qoqa_id @lang
  Scenario: Set the qoqa_ids on the languages
    Given I find a "res.lang" with code: fr_FR
    And having:
         | key     | value |
         | qoqa_id | 1     |
    Given I find a "res.lang" with code: de_DE
    And having:
         | key     | value |
         | qoqa_id | 2     |

  @qoqa_id @currency
  Scenario Outline: Set the qoqa_ids on the currencies
    Given I find a "res.currency" with oid: <oid>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | oid      | qoqa_id |
         | base.CHF | 1       |
         | base.EUR | 2       |
         | base.USD | 3       |
         | base.GBP | 4       |
         | base.CNY | 5       |
         | base.JPY | 6       |

  @qoqa_id @country
  Scenario Outline: Set the qoqa_ids on the Countries
    Given I find a "res.country" with oid: <oid>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | oid     | qoqa_id |
         | base.ch | 1       |
         | base.fr | 2       |
         | base.de | 3       |
         | base.it | 4       |
         | base.us | 5       |
         | base.uk | 6       |
         | base.dk | 7       |
         | base.nl | 8       |
         | base.be | 9       |
         | base.es | 10      |
         | base.pt | 11      |
         | base.cn | 12      |
         | base.jp | 14      |
         | base.li | 15      |
         | base.lu | 16      |
         | base.cy | 17      |

  @qoqa_id @tax
  Scenario Outline: Set the qoqa_ids on the taxes
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "account.tax" with description: <tax_code>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | tax_code | qoqa_id |
         | 2.5%     | 4       |
         | 3.8%     | 5       |
         | 8.0%     | 6       |
         | 0% excl. | 10      |

  @qoqa_id @tax
  Scenario Outline: Set the qoqa_ids on the taxes
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "account.tax" with description: <tax_code> and active: False
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | tax_code | qoqa_id |
         | 2.4%     | 1       |
         | 3.6%     | 2       |
         | 7.6%     | 3       |

  @qoqa_id @tax
  Scenario Outline: Set the qoqa_ids on the taxes
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I find a "account.tax" with description: <tax_code>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | tax_code | qoqa_id |
         | 2.1      | 7       |
         | 5.5      | 8       |
         | 19.6     | 9       |
