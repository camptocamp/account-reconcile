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
@delivery @setup

Feature: Configure the deliveries

  @partner
  Scenario Outline: create partners for delivery methods
  Given I need a "res.partner" with oid: <oid>
    And having:
         | key        | value                 |
         | name       | <name>                |
         | company_id | by oid: <company_oid> |
         | active     | <active>              |

    Examples: partners
      | oid                               | name                 | company_oid      | active |
      | scenario.partner_postlogistics    | PostLogistics        | scenario.qoqa_ch | 1      |
      | scenario.partner_postmail         | PostMail             | scenario.qoqa_ch | 1      |
      | scenario.partner_carrier_supplier | Supplier (delivery)  | scenario.qoqa_ch | 1      |
      | scenario.partner_legacy_fr        | Legacy FR (delivery) | scenario.qoqa_fr | 1      |
      | scenario.partner_lake_express     | Lake Express         | scenario.qoqa_ch | 0      |

  @carrier
  Scenario Outline: create delivery methods
  Given I need a "delivery.carrier" with oid: <oid>
    And having:
         | key        | value                                                |
         | name       | <name>                                               |
         | partner_id | <partner>                                            |
         | product_id | by oid: connector_ecommerce.product_product_shipping |
         | qoqa_id    | <qoqa_id>                                            |
         | active     | <active>                                             |

    Examples: carrier
      | oid                               | name                                      | partner                                                    | qoqa_id | active |
      | scenario.carrier_qoqa_free_ch     | QoQa Internal : Free CH                   | by name: QoQa Services SA                                  | 13      | 1      |
      | scenario.carrier_qoqa_free_fr     | QoQa Internal : Free fr                   | by name: QoQa Services France                              | 14      | 1      |
      | scenario.carrier_qoqa_liebherr    | QoQa Internal : Liebherr                  | by name: QoQa Services SA                                  | 27      | 0      |
      | scenario.carrier_pl_vino3         | PostLogistics CH : VinoLog - 3 bouteilles | by oid: delivery_carrier_label_postlogistics.postlogistics | 34      | 1      |
      | scenario.carrier_pl_alcool        | PostLogistics CH : PostAlcool             | by oid: delivery_carrier_label_postlogistics.postlogistics | 45      | 1      |
      | scenario.carrier_pl_big_spec49    | PostLogistics CH : Big Special 49         | by oid: delivery_carrier_label_postlogistics.postlogistics | 36      | 1      |
      | scenario.carrier_pl_light699      | PostLogistics CH : Light 699              | by oid: delivery_carrier_label_postlogistics.postlogistics | 24      | 1      |
      | scenario.carrier_pl_light_weight  | PostLogistics CH : Light Weight           | by oid: delivery_carrier_label_postlogistics.postlogistics | 16      | 1      |
      | scenario.carrier_pl_large         | PostLogistics CH : Large                  | by oid: delivery_carrier_label_postlogistics.postlogistics | 15      | 1      |
      | scenario.carrier_pl_vino_basic    | PostLogistics CH : VinoLog - Basic        | by oid: delivery_carrier_label_postlogistics.postlogistics | 22      | 1      |
      | scenario.carrier_pl_basic         | PostLogistics CH : Basic                  | by oid: delivery_carrier_label_postlogistics.postlogistics | 1       | 1      |
      | scenario.carrier_pl_vino_1_12     | PostLogistics CH : VinoLog 1/12           | by oid: delivery_carrier_label_postlogistics.postlogistics | 44      | 1      |
      | scenario.carrier_pl_advanced      | PostLogistics CH : Advanced               | by oid: delivery_carrier_label_postlogistics.postlogistics | 4       | 1      |
      | scenario.carrier_pl_big           | PostLogistics CH : Big                    | by oid: delivery_carrier_label_postlogistics.postlogistics | 3       | 1      |
      | scenario.carrier_pl_medium        | PostLogistics CH : Medium                 | by oid: delivery_carrier_label_postlogistics.postlogistics | 2       | 1      |
      | scenario.carrier_pm_medium        | PostMail : Medium                         | by oid: scenario.partner_postmail                          | 32      | 0      |
      | scenario.carrier_pm_7911          | PostMail : 7911                           | by oid: scenario.partner_postmail                          | 20      | 0      |
      | scenario.carrier_pm_small         | PostMail : Small                          | by oid: scenario.partner_postmail                          | 5       | 0      |
      | scenario.carrier_pm_small_small   | PostMail : SmallSmall                     | by oid: scenario.partner_postmail                          | 31      | 1      |
      | scenario.carrier_lfr_vin2fr       | Legacy FR : vin 2 fr                      | by oid: scenario.partner_legacy_fr                         | 33      | 0      |
      | scenario.carrier_lfr_dktbox       | Legacy FR : dktbox                        | by oid: scenario.partner_legacy_fr                         | 37      | 0      |
      | scenario.carrier_lfr_identique5   | Legacy FR : Identique5                    | by oid: scenario.partner_legacy_fr                         | 38      | 1      |
      | scenario.carrier_lfr_tnt10        | Legacy FR : TNT 10                        | by oid: scenario.partner_legacy_fr                         | 39      | 1      |
      | scenario.carrier_lfr_lettre355    | Legacy FR : Lettre 3-5-5                  | by oid: scenario.partner_legacy_fr                         | 43      | 1      |
      | scenario.carrier_lfr_vinsx3       | Legacy FR : Vins X3                       | by oid: scenario.partner_legacy_fr                         | 42      | 0      |
      | scenario.carrier_lfr_tnt579       | Legacy FR : TNT 579                       | by oid: scenario.partner_legacy_fr                         | 41      | 0      |
      | scenario.carrier_lfr_vinbouteille | Legacy FR : Vin à la bouteille            | by oid: scenario.partner_legacy_fr                         | 40      | 1      |
      | scenario.carrier_lfr_nookspec     | Legacy FR : Nook spécial                  | by oid: scenario.partner_legacy_fr                         | 18      | 0      |
      | scenario.carrier_lfr_10euros      | Legacy FR : 10 euros                      | by oid: scenario.partner_legacy_fr                         | 12      | 0      |
      | scenario.carrier_lfr_standard     | Legacy FR : Standard                      | by oid: scenario.partner_legacy_fr                         | 6       | 1      |
      | scenario.carrier_lfr_fraisport    | Legacy FR : + frais de port               | by oid: scenario.partner_legacy_fr                         | 17      | 1      |
      | scenario.carrier_lfr_light        | Legacy FR : Light                         | by oid: scenario.partner_legacy_fr                         | 10      | 0      |
      | scenario.carrier_lfr_7911         | Legacy FR : 7911                          | by oid: scenario.partner_legacy_fr                         | 21      | 1      |
      | scenario.carrier_lfr_lourd        | Legacy FR : Lourd                         | by oid: scenario.partner_legacy_fr                         | 23      | 1      |
      | scenario.carrier_lfr_nook         | Legacy FR : Nook                          | by oid: scenario.partner_legacy_fr                         | 19      | 0      |
      | scenario.carrier_lfr_vinfrance    | Legacy FR : Vin France                    | by oid: scenario.partner_legacy_fr                         | 25      | 1      |
      | scenario.carrier_lfr_identique7   | Legacy FR : Identique 7                   | by oid: scenario.partner_legacy_fr                         | 26      | 1      |
      | scenario.carrier_lfr_lourd2       | Legacy FR : lourd                         | by oid: scenario.partner_legacy_fr                         | 29      | 0      |
      | scenario.carrier_lfr_567          | Legacy FR : 567                           | by oid: scenario.partner_legacy_fr                         | 11      | 0      |
      | scenario.carrier_lke_basic        | Lake Express : Basic                      | by oid: scenario.partner_lake_express                      | 9       | 0      |
      | scenario.carrier_sup_bike         | Bike                                      | by oid: scenario.partner_carrier_supplier                  | 30      | 1      |
      | scenario.carrier_sup_special1     | Special1                                  | by oid: scenario.partner_carrier_supplier                  | 28      | 0      |
      | scenario.carrier_sup_big          | Big                                       | by oid: scenario.partner_carrier_supplier                  | 35      | 1      |
