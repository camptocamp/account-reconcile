# -*- coding: utf-8 -*-
@upgrade_to_1.7 @qoqa

Feature: upgrade to 1.7

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                    |
    Then my modules should have been installed and models reloaded

  Scenario Outline: add refund descriptions
    Given I need a "account.refund.description" with oid: scenario.refund_desc_<oid>
    And having:
      | key                       | value                    |
      | name                      | <name>                   |
    Examples: Refund description
      | oid            | name                           |
      | annul_commande | Annulation de commande         |
      | article_defect | Article défectueux             |
      | bug_paiement   | Bug paiement (à double etc)    |
      | casse          | Casse Poste / Vinolog          |
      | chgt_prix      | Changement de prix             |
      | non_livrable   | Commande non-livrable          |
      | retrait_place  | Commande retirée sur place     |
      | erreur_livr    | Erreur de livraison            |
      | non_reclame    | Non-réclamé - Restock          |
      | echange_taille | Pas d’échange taille           |
      | perte_poste    | Perte Poste                    |
      | non_conforme   | Qualité non conforme - attente |
      | rabais         | Rabais Qollabo                 |
      | rbmt_partiel   | Remboursement partiel          |
      | rembourse      | Satisfait ou remboursé         |

  Scenario: add final claim category to company
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | key                      | value                            |
      | unclaimed_final_categ_id | by name: Non-réclamé - 4. Résolu |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.7"
