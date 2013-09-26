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
@connector_qoqa @core_setup

Feature: Configure the connector's backend

  @qoqa_backend
  Scenario: Configure the QoQa backend
  Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    And having:
         | key             | value                      |
         | url             | https://ch.test02.qoqa.com |
         | default_lang_id | by code: fr_FR             |

  @automatic_workflows
  Scenario: Configure Sales Automatic Workflows
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.automatic_validation
    And having:
      | key              | value       |
      | picking_policy   | one         |
      | invoice_quantity | procurement |
      | order_policy     | picking     |
      | validate_order   | True        |
      | validate_invoice | True        |
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.manual_validation
    And having:
      | key              | value       |
      | picking_policy   | one         |
      | invoice_quantity | procurement |
      | order_policy     | picking     |
      | validate_order   | False       |
      | validate_invoice | True        |

  @sale_payment_methods_ch
  Given I need a "payment.method" with oid: scenario.payment_method_postfinance
    And having:
      | key                 | value                                                |
      | name                | Postfinance (CH)                                     |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_postfinance                 |
  Given I need a "payment.method" with oid: scenario.payment_method_visa_ch
    And having:
      | key                 | value                                                |
      | name                | Visa (CH)                                            |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_visa_ch                     |
  Given I need a "payment.method" with oid: scenario.payment_method_mastercard_ch
    And having:
      | key                 | value                                                |
      | name                | Mastercard (CH)                                      |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_mastercard_ch               |
  Given I need a "payment.method" with oid: scenario.payment_method_paypal_ch
    And having:
      | key                 | value                                                |
      | name                | Paypal (CH)                                          |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_paypal_ch                   |
  Given I need a "payment.method" with oid: scenario.payment_method_swissbilling
    And having:
      | key                 | value                                                |
      | name                | Swissbilling (paiement par facture) (CH)             |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_swissbilling                |

  @sale_payment_methods_ch_old
  Given I need a "payment.method" with oid: scenario.payment_method_swikey_ch_old
    And having:
      | key                 | value                                                |
      | name                | Swikey (CH) - plus utilisé                           |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_swikey_old                  |
  Given I need a "payment.method" with oid: scenario.payment_method_visa_postfinance_ch_old
    And having:
      | key                 | value                                                |
      | name                | Postfinance (CH) - plus utilisé                      |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_postfinance_old             |
  Given I need a "payment.method" with oid: scenario.payment_method_mastercard_ch_old
    And having:
      | key                 | value                                                |
      | name                | Mastercard (CH) - plus utilisé                       |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_mastercard_ch_old           |
  Given I need a "payment.method" with oid: scenario.payment_method_visa_ch_old
    And having:
      | key                 | value                                                |
      | name                | Visa (CH) - plus utilisé                             |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_visa_ch_old                 |

  @sale_payment_methods_fr
  Given I need a "payment.method" with oid: scenario.payment_method_carte_bleue
    And having:
      | key                 | value                                                |
      | name                | Carte Bleue Visa (FR)                                |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_carte_bleue                 |
  Given I need a "payment.method" with oid: scenario.payment_method_visa_fr
    And having:
      | key                 | value                                                |
      | name                | Visa (FR)                                            |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_visa_fr                     |
  Given I need a "payment.method" with oid: scenario.payment_method_mastercard_fr
    And having:
      | key                 | value                                                |
      | name                | Mastercard (FR)                                      |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_mastercard_fr               |
  Given I need a "payment.method" with oid: scenario.payment_method_paiement_3x_fr
    And having:
      | key                 | value                                                |
      | name                | Paiement 3x (FR)                                     |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_paiement_3x                 |
  Given I need a "payment.method" with oid: scenario.payment_method_paypal_fr
    And having:
      | key                 | value                                                |
      | name                | Paypal (FR)                                          |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_paypal_fr                   |

  @sale_payment_methods_fr_old
  Given I need a "payment.method" with oid: scenario.payment_method_carte_bleue_fr_old
    And having:
      | key                 | value                                                |
      | name                | Carte Bleue Visa (FR) - plus utilisé                 |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_carte_bleue_old             |
  Given I need a "payment.method" with oid: scenario.payment_method_visa_fr_old
    And having:
      | key                 | value                                                |
      | name                | Visa (FR) - plus utilisé                             |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_visa_fr_old                 |
  Given I need a "payment.method" with oid: scenario.payment_method_mastercard_fr_old
    And having:
      | key                 | value                                                |
      | name                | Mastercard (FR) - plus utilisé                       |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_mastercard_fr_old           |
  Given I need a "payment.method" with oid: scenario.payment_method_sogenactif_fr_old
    And having:
      | key                 | value                                                |
      | name                | ? Sogenactif (FR) - plus utilisé                     |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | by oid: scenario.journal_sogenactif_old              |
