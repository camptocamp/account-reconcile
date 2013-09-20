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
@logistic @core_setup

Feature: Setup the logistic for QoQa
  For each company, we need the following locations:
  SAV, Non-réclamé, Stock, Défectueux

  @location_ch_main
    Scenario: Assign the pre-existing main location to the swiss company
    Given I find a "stock.location" with oid: stock.stock_location_company
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |

  @location_ch_output
    Scenario: Assign the pre-existing output location to the swiss company
    Given I find a "stock.location" with oid: stock.stock_location_output
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |

  @location_ch_stock
    Scenario: Assign the pre-existing stock location to the swiss company
    Given I find a "stock.location" with oid: stock.stock_location_stock
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |

  @location_ch_sav
    Scenario: Create a "SAV" location for CH
    Given I need a "stock.location" with oid: scenario.location_ch_sav
    And having:
    | name        | value                                |
    | name        | SAV                                  |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |

  @location_ch_non_reclame
    Scenario: Create a "Non-réclamé" location for CH
    Given I need a "stock.location" with oid: scenario.location_ch_non_reclame
    And having:
    | name        | value                                |
    | name        | Non réclamé                          |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |

  @location_ch_defectueux
    Scenario: Create a "défectueux" location for CH
    Given I need a "stock.location" with oid: scenario.location_ch_non_reclame
    And having:
    | name        | value                                |
    | name        | Défectueux                           |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |

  @warehouse_ch
    Scenario: Assign the pre-existing warehouse to the swiss company
    Given I need a "stock.warehouse" with oid: stock.warehouse0
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |

  @shop_ch
    Scenario: Assign the pre-existing sale shop to the swiss company
    Given I need a "sale.shop" with oid: sale.sale_shop_1
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |
