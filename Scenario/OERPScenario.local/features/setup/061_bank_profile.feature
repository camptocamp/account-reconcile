@bank_profile @setup
Feature: BANK PROFILES

############################### COMPANY 1 ###############################

  Scenario Outline: BANK PROFILE
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
    | name                  | value                    |
    | name                  | <name>                   |
    | journal_id            | by name: <name>          |
    | commission_account_id | by code: 10900           |
    | balance_check         | 1                        |
    | import_type           | generic_csvxls_so        |
    | company_id            | by oid: scenario.qoqa_ch |
   And with following rules
    | name                                                                  |
    | Match from line reference (based on Invoice number)                   |
    | Match from line reference (based on Invoice Supplier number)          |
    | Match from line reference (based on SO number)                        |
    | Match from line label (based on partner field 'Bank Statement Label') |
    | Match from line label (based on partner name)                         |

   Examples: Bank profiles for QoQa CH
     | oid                       | name                                |
     | scenario.profile_ch_service_client   | Compte Service-client Qgroup        |
     | scenario.profile_ch_fournisseur_chf  | Compte Fournisseurs Qgroup          |
     | scenario.profile_ch_client_manuel    | Compte Client manuel Qgroup         |
     | scenario.profile_ch_enc_debiteur     | Compte Encaissement débiteur Qgroup |
     | scenario.profile_ch_fournisseur_eur  | Compte Fournisseur Qgroup en EUR    |
     | scenario.profile_ch_fournisseur_usd  | Compte Fournisseur Qgroup en USD    |
     #| scenario.profile_ch_projet_geelee_ch | Compte Projet Geelee.ch             |
     | scenario.profile_ch_salaires         | Compte Paiement Salaires            |
     | scenario.profile_ch_epargne          | Compte épargne                      |
     | scenario.profile_ch_garantie_loyer   | Compte garantie loyer               |

  Scenario Outline: BANK PROFILE FOR PAYMENT IMPORT
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
    | name                  | value                      |
    | name                  | <name>                     |
    | journal_id            | by name: <name>            |
    | commission_account_id | by code: <account>         |
    | receivable_account_id | by code: <receivable_acc>  |
    | balance_check         | 0                          |
    | import_type           | generic_csvxls_transaction |
    | company_id            | by oid: scenario.qoqa_ch   |
   And with following rules
    | name                                                |
    | Match from line reference (based on transaction ID) |
    | Match from line reference (based on SO number)      |

   Examples: Bank import for QoQa CH
     | oid                                           | name                      | account | receivable_acc |
     | scenario.profile_import_cb_postfinance        | Import CB Postfinance     |   10900 |          11000 |
     | scenario.profile_import_visa_mastercard_ch    | Import Visa / Mastercard  |   32930 |          11010 |
     | scenario.profile_paypal_ch                    | Paypal                    |   32930 |                |
     | scenario.profile_reglement_cb_postfinance     | Reglement Postfinance     |   10900 |          11030 |
     | scenario.profile_reglement_visa_mastercard_ch | Reglement Visa Mastercard |   10900 |          11030 |




  Scenario Outline: BANK PROFILE FOR PAYMENT IMPORT FOR QOQA FR
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
    | name                  | value                      |
    | name                  | <name>                     |
    | journal_id            | by name: <name>            |
    | commission_account_id | by code: <account>         |
    | receivable_account_id | by code: <receivable_acc>  |
    | balance_check         | 0                          |
    | import_type           | generic_csvxls_transaction |
    | company_id            | by oid: scenario.qoqa_fr   |
   And with following rules
    | name                                                |
    | Match from line reference (based on transaction ID) |
    | Match from line reference (based on SO number)      |

   Examples: Bank import for QoQa CH
     | oid                                              | name                      | account | receivable_acc |
     | scenario.profile_import_fr_carte_bleue           | Import CB                 |   627800|         411002 |
     | scenario.profile_import_fr_visa                  | Import Visa               |   627800|         411002 |
     | scenario.profile_import_fr_mastercard            | Import Mastercard         |   627800|         411002 |
     | scenario.profile_import_fr_paiement_3x           | Import Paiement 3x        |   627800|         411002 |
     | scenario.profile_import_fr_paypal                | Import Paypal             |   627800|         411002 |
     | scenario.profile_reglement_fr_carte_bleue        | Import CB                 |   471000|         411002 |
     | scenario.profile_reglement_fr_visa               | Règlement Visa            |   471000|         411001 |
     | scenario.profile_reglement_fr_mastercard         | Règlement Mastercard      |   471000|         411001 |
     | scenario.profile_reglement_fr_paiement_3x        | Règlement Paiement 3x     |   471000|         411001 |
     | scenario.profile_reglement_fr_paypal             | Règlement Paypal          |   471000|         411001 | 
     
     
  Scenario Outline: BANK PROFILE FOR QOQA FR
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
    | name                  | value                    |
    | name                  | <name>                   |
    | journal_id            | by name: <name>          |
    | commission_account_id | by code: 471000          |
    | balance_check         | 1                        |
    | import_type           | generic_csvxls_so        |
    | company_id            | by oid: scenario.qoqa_fr |
   And with following rules
    | name                                                                  |
    | Match from line reference (based on Invoice number)                   |
    | Match from line reference (based on Invoice Supplier number)          |
    | Match from line reference (based on SO number)                        |
    | Match from line label (based on partner field 'Bank Statement Label') |
    | Match from line label (based on partner name)                         |

   Examples: Bank profiles for QoQa CH
     | oid                              | name              |
     | scenario.profile_banque_fr_bnp   | BNP               |
  
     
         
