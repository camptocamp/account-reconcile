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

  @shop_label_logo
  Scenario: I set a label logo on shops
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qoqa_ch
    And I set a postlogistics label logo from file "images/qoqa_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qwine_ch
    And I set a postlogistics label logo from file "images/qwine_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qsport_ch
    And I set a postlogistics label logo from file "images/qsport_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qstyle_ch
    And I set a postlogistics label logo from file "images/qstyle_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qooking_ch
    And I set a postlogistics label logo from file "images/qooking_label.png"

  @postlogistics_config
  Scenario: I configure postlogistics authentification
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | name                                | value                       |
      | postlogistics_username              | TU_9272_06                  |
      | postlogistics_password              | x1KsSvyY6X                  |
      | postlogistics_license_less_1kg      | 60035471                    |
      | postlogistics_license_more_1kg      | 60035471                    |
      | postlogistics_license_vinolog       | 60035471                    |
      | postlogistics_office                | 1030 Bussigny-près-Lausanne |
      | postlogistics_default_label_layout  | by code: A7                 |
      | postlogistics_default_output_format | by code: PDF                |
      | postlogistics_default_resolution    | by code: 300                |

  @postlogistics_options_update
  Scenario: I update postlogistics services (It will take 1 minute)
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And I update postlogistics services

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
      | scenario.partner_postmail         | PostMail             | scenario.qoqa_ch | 1      |
      | scenario.partner_colissimo        | Colissimo            | scenario.qoqa_fr | 1      |
      | scenario.partner_carrier_supplier | Supplier (delivery)  | scenario.qoqa_ch | 1      |
      | scenario.partner_legacy_fr        | Legacy FR (delivery) | scenario.qoqa_fr | 1      |
      | scenario.partner_lake_express     | Lake Express         | scenario.qoqa_ch | 0      |

  @carrier @rate
  Scenario Outline: create delivery methods for rates
  Given I need a "delivery.carrier" with oid: <oid>
    And having:
         | key        | value                                                |
         | name       | <name>                                               |
         | partner_id | <partner>                                            |
         | product_id | by oid: connector_ecommerce.product_product_shipping |
         | active     | <active>                                             |
         | qoqa_type  | rate                                                 |

    Examples: carrier
      | oid                               | name                                      | partner                                                    | active |
      | scenario.carrier_qoqa_free_ch     | QoQa Internal : Free CH                   | by name: QoQa Services SA                                  | 1      |
      | scenario.carrier_qoqa_free_fr     | QoQa Internal : Free fr                   | by name: QoQa Services France                              | 1      |
      | scenario.carrier_qoqa_liebherr    | QoQa Internal : Liebherr                  | by name: QoQa Services SA                                  | 0      |
      | scenario.carrier_pl_vino3         | PostLogistics CH : VinoLog - 3 bouteilles | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_alcool        | PostLogistics CH : PostAlcool             | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_big_spec49    | PostLogistics CH : Big Special 49         | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_light699      | PostLogistics CH : Light 699              | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_light_weight  | PostLogistics CH : Light Weight           | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_large         | PostLogistics CH : Large                  | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_vino_basic    | PostLogistics CH : VinoLog - Basic        | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_basic         | PostLogistics CH : Basic                  | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_vino_1_12     | PostLogistics CH : VinoLog 1/12           | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_advanced      | PostLogistics CH : Advanced               | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_big           | PostLogistics CH : Big                    | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pl_medium        | PostLogistics CH : Medium                 | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      |
      | scenario.carrier_pm_medium        | PostMail : Medium                         | by oid: scenario.partner_postmail                          | 0      |
      | scenario.carrier_pm_7911          | PostMail : 7911                           | by oid: scenario.partner_postmail                          | 0      |
      | scenario.carrier_pm_small         | PostMail : Small                          | by oid: scenario.partner_postmail                          | 0      |
      | scenario.carrier_pm_small_small   | PostMail : SmallSmall                     | by oid: scenario.partner_postmail                          | 1      |
      | scenario.carrier_lfr_vin2fr       | Legacy FR : vin 2 fr                      | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_dktbox       | Legacy FR : dktbox                        | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_identique5   | Legacy FR : Identique5                    | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_tnt10        | Legacy FR : TNT 10                        | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_lettre355    | Legacy FR : Lettre 3-5-5                  | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_vinsx3       | Legacy FR : Vins X3                       | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_tnt579       | Legacy FR : TNT 579                       | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_vinbouteille | Legacy FR : Vin à la bouteille            | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_nookspec     | Legacy FR : Nook spécial                  | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_10euros      | Legacy FR : 10 euros                      | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_standard     | Legacy FR : Standard                      | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_fraisport    | Legacy FR : + frais de port               | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_light        | Legacy FR : Light                         | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_7911         | Legacy FR : 7911                          | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_lourd        | Legacy FR : Lourd                         | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_nook         | Legacy FR : Nook                          | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_vinfrance    | Legacy FR : Vin France                    | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_identique7   | Legacy FR : Identique 7                   | by oid: scenario.partner_legacy_fr                         | 1      |
      | scenario.carrier_lfr_lourd2       | Legacy FR : lourd                         | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lfr_567          | Legacy FR : 567                           | by oid: scenario.partner_legacy_fr                         | 0      |
      | scenario.carrier_lke_basic        | Lake Express : Basic                      | by oid: scenario.partner_lake_express                      | 0      |
      | scenario.carrier_sup_bike         | Bike                                      | by oid: scenario.partner_carrier_supplier                  | 1      |
      | scenario.carrier_sup_special1     | Special1                                  | by oid: scenario.partner_carrier_supplier                  | 0      |
      | scenario.carrier_sup_big          | Big                                       | by oid: scenario.partner_carrier_supplier                  | 1      |

  @qoqa_id @rate
  Scenario Outline: create bindings for rate
  Given I need a "qoqa.shipper.rate" with oid: <oid>
    And having:
         | key        | value                                                |
         | openerp_id | by oid: <carrier_oid>                                |
         | qoqa_id    | <qoqa_id>                                            |

    Examples: bindings
      | oid                                    | carrier_oid                       | qoqa_id |
      | scenario.shipper_rate_qoqa_free_ch     | scenario.carrier_qoqa_free_ch     | 13      |
      | scenario.shipper_rate_qoqa_free_fr     | scenario.carrier_qoqa_free_fr     | 14      |
      | scenario.shipper_rate_qoqa_liebherr    | scenario.carrier_qoqa_liebherr    | 27      |
      | scenario.shipper_rate_pl_vino3         | scenario.carrier_pl_vino3         | 34      |
      | scenario.shipper_rate_pl_alcool        | scenario.carrier_pl_alcool        | 45      |
      | scenario.shipper_rate_pl_big_spec49    | scenario.carrier_pl_big_spec49    | 36      |
      | scenario.shipper_rate_pl_light699      | scenario.carrier_pl_light699      | 24      |
      | scenario.shipper_rate_pl_light_weight  | scenario.carrier_pl_light_weight  | 16      |
      | scenario.shipper_rate_pl_large         | scenario.carrier_pl_large         | 15      |
      | scenario.shipper_rate_pl_vino_basic    | scenario.carrier_pl_vino_basic    | 22      |
      | scenario.shipper_rate_pl_basic         | scenario.carrier_pl_basic         | 1       |
      | scenario.shipper_rate_pl_vino_1_12     | scenario.carrier_pl_vino_1_12     | 44      |
      | scenario.shipper_rate_pl_advanced      | scenario.carrier_pl_advanced      | 4       |
      | scenario.shipper_rate_pl_big           | scenario.carrier_pl_big           | 3       |
      | scenario.shipper_rate_pl_medium        | scenario.carrier_pl_medium        | 2       |
      | scenario.shipper_rate_pm_medium        | scenario.carrier_pm_medium        | 32      |
      | scenario.shipper_rate_pm_7911          | scenario.carrier_pm_7911          | 20      |
      | scenario.shipper_rate_pm_small         | scenario.carrier_pm_small         | 5       |
      | scenario.shipper_rate_pm_small_small   | scenario.carrier_pm_small_small   | 31      |
      | scenario.shipper_rate_lfr_vin2fr       | scenario.carrier_lfr_vin2fr       | 33      |
      | scenario.shipper_rate_lfr_dktbox       | scenario.carrier_lfr_dktbox       | 37      |
      | scenario.shipper_rate_lfr_identique5   | scenario.carrier_lfr_identique5   | 38      |
      | scenario.shipper_rate_lfr_tnt10        | scenario.carrier_lfr_tnt10        | 39      |
      | scenario.shipper_rate_lfr_lettre355    | scenario.carrier_lfr_lettre355    | 43      |
      | scenario.shipper_rate_lfr_vinsx3       | scenario.carrier_lfr_vinsx3       | 42      |
      | scenario.shipper_rate_lfr_tnt579       | scenario.carrier_lfr_tnt579       | 41      |
      | scenario.shipper_rate_lfr_vinbouteille | scenario.carrier_lfr_vinbouteille | 40      |
      | scenario.shipper_rate_lfr_nookspec     | scenario.carrier_lfr_nookspec     | 18      |
      | scenario.shipper_rate_lfr_10euros      | scenario.carrier_lfr_10euros      | 12      |
      | scenario.shipper_rate_lfr_standard     | scenario.carrier_lfr_standard     | 6       |
      | scenario.shipper_rate_lfr_fraisport    | scenario.carrier_lfr_fraisport    | 17      |
      | scenario.shipper_rate_lfr_light        | scenario.carrier_lfr_light        | 10      |
      | scenario.shipper_rate_lfr_7911         | scenario.carrier_lfr_7911         | 21      |
      | scenario.shipper_rate_lfr_lourd        | scenario.carrier_lfr_lourd        | 23      |
      | scenario.shipper_rate_lfr_nook         | scenario.carrier_lfr_nook         | 19      |
      | scenario.shipper_rate_lfr_vinfrance    | scenario.carrier_lfr_vinfrance    | 25      |
      | scenario.shipper_rate_lfr_identique7   | scenario.carrier_lfr_identique7   | 26      |
      | scenario.shipper_rate_lfr_lourd2       | scenario.carrier_lfr_lourd2       | 29      |
      | scenario.shipper_rate_lfr_567          | scenario.carrier_lfr_567          | 11      |
      | scenario.shipper_rate_lke_basic        | scenario.carrier_lke_basic        | 9       |
      | scenario.shipper_rate_sup_bike         | scenario.carrier_sup_bike         | 30      |
      | scenario.shipper_rate_sup_special1     | scenario.carrier_sup_special1     | 28      |
      | scenario.shipper_rate_sup_big          | scenario.carrier_sup_big          | 35      |


  @carrier @service
  Scenario Outline: create delivery methods for services
  Given I need a "delivery.carrier" with oid: <oid>
    And having:
         | key                            | value                                                |
         | name                           | <name>                                               |
         | partner_id                     | <partner>                                            |
         | product_id                     | by oid: connector_ecommerce.product_product_shipping |
         | active                         | <active>                                             |
         | qoqa_type                      | service                                              |

    Examples: services
      | oid                                  | name                | partner                       | active |
      | scenario.carrier_manualundefined     | (manual/undefined)  | by name: QoQa Services SA     | 1      |
      | scenario.carrier_legacy_fr           | Legacy FR           | by name: QoQa Services France | 1      |
      | scenario.carrier_manual_wphone       | Manual w/phone      | by name: QoQa Services SA     | 1      |
      | scenario.carrier_standard            | Standard            | by name: QoQa Services SA     | 1      |
      | scenario.carrier_standard_wphone     | Standard w/phone    | by name: QoQa Services SA     | 1      |
      | scenario.carrier_legacy_qwfr         | Legacy QWFR         | by name: QoQa Services France | 1      |
      | scenario.carrier_so_colissimo        | So Colissimo        | by name: QoQa Services France | 1      |
      | scenario.carrier_client_appointments | Client appointments | by name: QoQa Services SA     | 1      |
      | scenario.carrier_wine_transport      | Wine Transport      | by name: QoQa Services SA     | 1      |

  @carrier @service @postlogistic
  Scenario Outline: create delivery methods for services
  Given I need a "delivery.carrier" with oid: <oid>
    And having:
         | key                            | value                                                |
         | name                           | <name>                                               |
         | partner_id                     | <partner>                                            |
         | product_id                     | by oid: connector_ecommerce.product_product_shipping |
         | active                         | <active>                                             |
         | qoqa_type                      | service                                              |
         | type                           | <type>                                               |
         | postlogistics_service_group_id | by name: <service_name>                              |

    Examples: services
      | oid                                    | name                     | partner                                                    | active | type          | service_name                  |
      | scenario.carrier_postpac_prisi_std     | PostPac PRI+SI Std       | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Parcel                        |
      | scenario.carrier_postpac_prisi_man     | PostPac PRI+SI MAN       | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Parcel                        |
      | scenario.carrier_postpac_prisi_sp      | PostPac PRI+SI SP        | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Parcel                        |
      | scenario.carrier_amail_b5_0100g_02cm   | A-Mail B5 0-100g 0-2cm   | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Letters with barcode domestic |
      | scenario.carrier_amail_b5_0100g_25cm   | A-Mail B5 0-100g 2-5cm   | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Letters with barcode domestic |
      | scenario.carrier_amail_b5_100250g_02cm | A-Mail B5 100-250g 0-2cm | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Letters with barcode domestic |
      | scenario.carrier_amail_b5_100250g_25cm | A-Mail B5 100-250g 2-5cm | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Letters with barcode domestic |
      | scenario.carrier_vinolog               | VinoLog                  | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Solutions                     |
      | scenario.carrier_postpac_pri           | PostPac PRI              | by oid: delivery_carrier_label_postlogistics.postlogistics | 1      | postlogistics | Parcel                        |

  @qoqa_id @service
  Scenario Outline: create bindings for services
  Given I need a "qoqa.shipper.service" with oid: <oid>
    And having:
         | key        | value                                                |
         | openerp_id | by oid: <carrier_oid>                                |
         | qoqa_id    | <qoqa_id>                                            |

    Examples: bindings
      | oid                                            | carrier_oid                            | qoqa_id |
      | scenario.shipper_service_manualundefined       | scenario.carrier_manualundefined       | 1       |
      | scenario.shipper_service_postpac_prisi_std     | scenario.carrier_postpac_prisi_std     | 2       |
      | scenario.shipper_service_postpac_prisi_man     | scenario.carrier_postpac_prisi_man     | 3       |
      | scenario.shipper_service_postpac_prisi_sp      | scenario.carrier_postpac_prisi_sp      | 4       |
      | scenario.shipper_service_amail_b5_0100g_02cm   | scenario.carrier_amail_b5_0100g_02cm   | 5       |
      | scenario.shipper_service_amail_b5_0100g_25cm   | scenario.carrier_amail_b5_0100g_25cm   | 6       |
      | scenario.shipper_service_amail_b5_100250g_02cm | scenario.carrier_amail_b5_100250g_02cm | 7       |
      | scenario.shipper_service_amail_b5_100250g_25cm | scenario.carrier_amail_b5_100250g_25cm | 8       |
      | scenario.shipper_service_legacy_fr             | scenario.carrier_legacy_fr             | 9       |
      | scenario.shipper_service_wine_transport        | scenario.carrier_wine_transport        | 10      |
      | scenario.shipper_service_vinolog               | scenario.carrier_vinolog               | 11      |
      | scenario.shipper_service_manual_wphone         | scenario.carrier_manual_wphone         | 12      |
      | scenario.shipper_service_standard              | scenario.carrier_standard              | 13      |
      | scenario.shipper_service_standard_wphone       | scenario.carrier_standard_wphone       | 14      |
      | scenario.shipper_service_legacy_qwfr           | scenario.carrier_legacy_qwfr           | 15      |
      | scenario.shipper_service_postpac_pri           | scenario.carrier_postpac_pri           | 16      |
      | scenario.shipper_service_so_colissimo          | scenario.carrier_so_colissimo          | 17      |
      | scenario.shipper_service_client_appointments   | scenario.carrier_client_appointments   | 18      |

  @carrier_postlogistics_options
  Scenario Outline: I setup a postlogistic carrier options
    Given I need a "delivery.carrier.option" with oid: <oid>
    And having:
      | name           | value             |
      | carrier_id     | by oid: <carrier> |
      | tmpl_option_id | by code: <option> |
      | state          | <state>           |

    Examples: carrier options for PRI,SP
      | oid                              | carrier                           | option | state     |
      | scenario.carrier_option_1_pri_sp | scenario.carrier_postpac_prisi_sp | PRI,SP | mandatory |

      | scenario.carrier_option_1_a5     | scenario.carrier_postpac_prisi_sp | A5     | option    |
      | scenario.carrier_option_1_a6     | scenario.carrier_postpac_prisi_sp | A6     | option    |

    Examples: carrier options for Vinolog
      | oid                               | carrier                  | option | state     |
      | scenario.carrier_option_1_vinolog | scenario.carrier_vinolog | VL     | mandatory |

      | scenario.carrier_option_1_a5      | scenario.carrier_vinolog | A5     | option    |
      | scenario.carrier_option_1_a6      | scenario.carrier_vinolog | A6     | option    |
