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
@crm  @setup

Feature: CRM CLAIM SETTING FOR QOQA
   As an administrator, I do the following installation steps.

# Create an alias per alias in gmail to affect the right team
  @crm_alias_mail_create
  Scenario Outline: Create alias
    Given I need a "mail.alias" with oid: <oid>
      And having:
        | name             | value                    |
        | alias_name       | <name>                   |
        | alias_model_id   | by name: Claim           |
        | alias_user_id   | False                    |
  Examples: Create all basic test suggested sales team
        | oid                                   | name      |
        | scenario.crm_alias_test_qooking       | test.qooking   |
        | scenario.crm_alias_test_qsport        | test.qsport    |
        | scenario.crm_alias_test_qsyle         | test.qstyle    |
        | scenario.crm_alias_test_qwine         | test.qwine     |
        | scenario.crm_alias_test_qwine-fr      | test.qwine-fr     |
        | scenario.crm_alias_test_qooqa         | test.qoqa      |
        | scenario.crm_alias_test_qooqa-fr      | test.qoqa-fr      |
  Examples: Create all basic alias compared to mail per environnement
  # TODO : Update the qa and prod aliases !
        | oid                              | name              |
        | scenario.crm_alias_dev           | c2copenerp        |
        | scenario.crm_alias_test          | erp.test          |
        | scenario.crm_alias_qa            | erp.qa            |
        | scenario.crm_alias_prod          | erp.prod          |

  @crm_alias_mail_configure
  Scenario: Configure aliases
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qooking
    And I setup the shop to "Qooking.ch"
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qsport
    And I setup the shop to "Qsport.ch"
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qsyle
    And I setup the shop to "Qstyle.ch"
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qwine
    And I setup the shop to "Qwine.ch"
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qooqa
    And I setup the shop to "QoQa.ch"
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qwine-fr
    And I setup the shop to "Qwine.fr"
    Given I need a "mail.alias" with oid: scenario.crm_alias_test_qooqa-fr
    And I setup the shop to "QoQa.fr"


  @crm_case_section_sale_team
  Scenario Outline: Create sales team
    Given I need a "crm.case.section" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | parent_id  | by oid: crm.section_sales_department |
  Examples: Create all basic sales team
        | oid                                        | name      |
        | scenario.section_sale_team_commandes       | Commandes   |
        | scenario.section_sale_team_livr            | Livraisons   |
        | scenario.section_sale_team_cmpt_client     | Compte Client   |
        | scenario.section_sale_team_rma             | RMA/DOA   |
        | scenario.section_sale_team_loutre_plais    | Loutre plaisir   |
        | scenario.section_sale_team_qdefi           | Qdéfi   |
        | scenario.section_sale_team_loutre_dev      | Loutre Dév (pb technique)   |
        | scenario.section_sale_team_rep_mailing     | Réponse mailing   |
        | scenario.section_sale_team_sugg_article    | Suggestion articles   |
        | scenario.section_sale_team_rh              | RH Dossier   |
        | scenario.section_sale_team_sponsoring      | Sponsoring   |
        | scenario.section_sale_team_bestellung      | [DE] Bestellungen   |
        | scenario.section_sale_team_lieferung       | [DE] Lieferung   |
        | scenario.section_sale_team_rma_de          | [DE] RMA/DOA   |
      
  @crm_case_category_for_commandes
  Scenario Outline: Create category
    Given I need a "crm.case.categ" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | section_id  | by oid: scenario.section_sale_team_commandes |
        | object_id   | by name: Claim |
    Examples: Create all basic category
        | oid                                        | name      |
        | scenario.categ_1  | Annulation |
        | scenario.categ_2  | Bons  |
        | scenario.categ_3  | Hôtels  |
        | scenario.categ_4  | Intérêt article/commande manuelle |
        | scenario.categ_5  | Modification de commande  |
        | scenario.categ_6  | Mailing (code)  |
        | scenario.categ_7  | Paiement  |
  
  @crm_case_category_for_livraisons
  Scenario Outline: Create category
  
    Given I need a "crm.case.categ" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | section_id  | by oid: scenario.section_sale_team_livr |
        | object_id   | by name: Claim |
    Examples: Create all basic category
        | oid                                        | name      |
        | scenario.categ_9  | Casse marchandise |
        | scenario.categ_10 | Livraison incomplète  |
        | scenario.categ_11 | Délai de livraison  |
        | scenario.categ_12 | Erreur de livraison - article à renvoyer  |
        | scenario.categ_13 | Vacances - livraison différée |
        | scenario.categ_14 | Regroupement de commande  |
        | scenario.categ_15 | Non-réclamé |
        | scenario.categ_16 | Perte Poste |

  @crm_case_category_for_rma
  Scenario Outline: Create category
    Given I need a "crm.case.categ" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | section_id  | by oid: scenario.section_sale_team_rma |
        | object_id   | by name: Claim |
    Examples: Create all basic category
        | oid                                        | name      |
        | scenario.categ_20 | Attente marchandise |
        | scenario.categ_21 | Attente réponse fournisseur |
        | scenario.categ_22 | Cas délicats  |
        | scenario.categ_23 | Procédure renvoi  |
        | scenario.categ_24 | Problème de taille - retour article |
        | scenario.categ_25 | Echanges/remboursement/bon  |
  
  @crm_case_category_for_loutre_plais
  Scenario Outline: Create category
    Given I need a "crm.case.categ" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | section_id  | by oid: scenario.section_sale_team_loutre_plais |
        | object_id   | by name: Claim |
    Examples: Create all basic category
        | oid                                        | name      |
        | scenario.categ_27 | Events  |

  @crm_case_category_for_sugg_article
  Scenario Outline: Create category
    Given I need a "crm.case.categ" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | section_id  | by oid: scenario.section_sale_team_sugg_article |
        | object_id   | by name: Claim |
    Examples: Create all basic category
        | oid                                        | name      |
        | scenario.categ_35 | Proposition |
        | scenario.categ_36 | Echantillon fournisseur |




