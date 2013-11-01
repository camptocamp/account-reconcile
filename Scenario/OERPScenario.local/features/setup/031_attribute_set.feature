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
@attribute_set @setup

Feature: Configure the attribute sets

  @template_attributes
  Scenario Outline: Create attributes for product templates
  Given I need a "attribute.attribute" with oid: scenario.attr_<name>
    And I set the attribute model to oid: procurement.model_product_template
    And having:
        | key               | value                               |
        | name              | x_<name>                            |
        | field_description | <descr>                             |
        | attribute_type    | <type>                              |
        | translate         | <translate>                         |
        | required_on_views | <required>                          |

  Examples: Template attributes
      | name       | descr      | type | translate | required |
      | brand      | Brand      | char | True      | False    |
      | highlights | Highlights | text | True      | False    |

  Examples: Template attributes for the wine (or liquor)
      | name         | descr       | type   | translate | required |
      | winemaker    | Winemaker   | select | False     | True     |
      | appellation  | Appellation | char   | False     | True     |
      | millesime    | Millesime   | char   | False     | False    |
      | wine_region  | Region      | char   | False     | False    |
      | wine_type    | Type        | select | False     | True     |

  Examples: Template attributes for the liquor (or liquor)
      | name   | descr             | type  | translate | required |
      | ageing | Ageing            | float | False     | False    |
      | abv    | Alcohol by volume | float | False     | False    |

  @country_options
  Scenario: Create the options for the country attribute
  Given I need a "attribute.attribute" with oid: scenario.attr_country_id
    And I set the attribute model to oid: procurement.model_product_template
    And having:
        | key               | value                               |
        | name              | x_country_id                        |
        | field_description | Country                             |
        | attribute_type    | select                              |
        | required_on_views | True                                |
        | relation          | res.country                         |
        | relation_model_id | by oid: base.model_res_country      |
    And I generate the attribute options from the model res.country

  @wine_type_options
  Scenario Outline: Create the options for the wine_type attribute
  Given I need a "attribute.option" with oid: scenario.attr_option_wine_type_<oid>
    And having:
        | key          | value                            |
        | name         | <name>                           |
        | attribute_id | by oid: scenario.attr_wine_type  |
        | sequence     | <sequence>                       |

  Examples: Options
      | oid      | name     | sequence |
      | white    | Blanc    | 0        |
      | red      | Rouge    | 1        |
      | rose     | Rosé     | 2        |
      | mousseux | Mousseux | 3        |
      | other    | Autre    | 4        |

  @wine_class_id_options
  Scenario: Create the options for the wine_class_id attribute
  Given I need a "attribute.attribute" with oid: scenario.attr_wine_class_id
    And having:
        | key               | value                                                       |
        | field_id          | by oid: wine_ch_report.field_product_template_wine_class_id |
        | attribute_type    | select                                                      |
        | relation_model_id | by oid: wine_ch_report.model_wine_class                     |
    And I generate the attribute options from the model wine.class

  @wine_bottle_id_options
  Scenario: Create the options for the wine_bottle_id attribute
  Given I need a "attribute.attribute" with oid: scenario.attr_wine_bottle_id
    And having:
        | key               | value                                                        |
        | field_id          | by oid: wine_ch_report.field_product_template_wine_bottle_id |
        | attribute_type    | select                                                       |
        | relation_model_id | by oid: wine_ch_report.model_wine_bottle                     |
    And I generate the attribute options from the model wine.bottle

  @variant_attributes
  Scenario Outline: Create attributes for product products
  Given I need a "attribute.attribute" with oid: scenario.attr_<name>
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key               | value                               |
        | name              | x_<name>                            |
        | field_description | <descr>                             |
        | attribute_type    | <type>                              |
        | translate         | <translate>                         |
        | required_on_views | <required>                          |

  Examples: Variant attributes
      | name             | descr            | type      | translate | required |
      | warranty         | Warranty         | integer   | False     | True     |
      | dimension_big    | Dimension big    | float     | True      | False    |
      | dimension_medium | Dimension medium | float     | False     | False    |
      | dimension_small  | Dimension small  | float     | False     | False    |
      | variant_weight   | Variant Weight   | float     | False     | False    |
      # warranty will probably change for the RMA

  @general
  Scenario: Create a general attribute set
  Given I find a "attribute.set" with oid: qoqa_base_data.set_general
  Given I need a "attribute.group" with oid: scenario.group_general_main
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                              |
        | name             | Caractéristiques principales       |
        | attribute_set_id | by oid: qoqa_base_data.set_general |

  @general_groups @general
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_main_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_general_main    |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: General Main Groups
      | attribute_name   | sequence |
      | brand            | 0        |
      | highlights       | 1        |
      | warranty         | 2        |
      | dimension_big    | 3        |
      | dimension_medium | 4        |
      | dimension_small  | 5        |
      | variant_weight   | 6        |


  @wine
  Scenario: Create an attribute set for wine
  Given I find a "attribute.set" with oid: qoqa_base_data.set_wine
  Given I need a "attribute.group" with oid: scenario.group_wine_main
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                           |
        | name             | Caractéristiques principales    |
        | attribute_set_id | by oid: qoqa_base_data.set_wine |
  Given I need a "attribute.group" with oid: scenario.group_wine_wine
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                           |
        | name             | Caractéristiques du vin         |
        | attribute_set_id | by oid: qoqa_base_data.set_wine |

  @wine_group_general @wine
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_wine_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_wine_main       |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: Wine Main Group
      | attribute_name   | sequence |
      | brand            | 0        |
      | highlights       | 1        |
      | warranty         | 2        |
      | dimension_big    | 3        |
      | dimension_medium | 4        |
      | dimension_small  | 5        |
      | variant_weight   | 6        |

  @wine_group_wine @wine
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_wine_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_wine_wine       |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: Wine Group
       | attribute_name | sequence |
       | winemaker      | 10       |
       | appellation    | 11       |
       | millesime      | 13       |
       | country_id     | 15       |
       | wine_region    | 16       |
       | wine_bottle_id | 17       |
       | wine_type      | 18       |
       | wine_class_id  | 19       |

  @liquor
  Scenario: Create an attribute set for liquor
  Given I find a "attribute.set" with oid: qoqa_base_data.set_liquor
  Given I need a "attribute.group" with oid: scenario.group_liquor_main
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                             |
        | name             | Caractéristiques principales      |
        | attribute_set_id | by oid: qoqa_base_data.set_liquor |
  Given I need a "attribute.group" with oid: scenario.group_liquor_liquor
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                             |
        | name             | Caractéristiques du spiritueux    |
        | attribute_set_id | by oid: qoqa_base_data.set_liquor |

  @liquor_group_general @liquor
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_liquor_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_liquor_main     |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: liquor Main Group
      | attribute_name   | sequence |
      | brand            | 0        |
      | highlights       | 1        |
      | warranty         | 2        |
      | dimension_big    | 3        |
      | dimension_medium | 4        |
      | dimension_small  | 5        |
      | variant_weight   | 6        |

  @liquor_group_liquor @liquor
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_liquor_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_liquor_liquor   |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: liquor Group
       | attribute_name | sequence |
       | winemaker      | 10       |
       | appellation    | 11       |
       | millesime      | 12       |
       | ageing         | 13       |
       | country_id     | 14       |
       | abv            | 15       |
