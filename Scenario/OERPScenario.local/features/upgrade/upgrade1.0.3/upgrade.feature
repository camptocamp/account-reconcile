# -*- coding: utf-8 -*-
@upgrade_from_1.0.2 @qoqa

Feature: upgrade to 1.0.3

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                |
      | ecotax                              |
      | qoqa_offer                          |
      | connector_qoqa                      |
      | specific_fct                        |
      | sale_payment_method                 |
      | sale_automatic_workflow             |
      | connector                           |
    Then my modules should have been installed and models reloaded

  @ecotax
  Scenario: Activate the ecotax checkbox on the ecotax taxes
    Given I execute the SQL commands
    """
    UPDATE account_tax SET ecotax = TRUE WHERE name LIKE '%TAR%';
    UPDATE qoqa_offer_position SET ecotax_id = (SELECT id FROM account_tax WHERE amount = qoqa_offer_position.ecotax / 100 AND ecotax IS TRUE) WHERE ecotax > 0;
    """

  @attribute @highlights
  Scenario: Remove the 'highlights' attribute
    Given I find a "attribute.attribute" with name: x_highlights
    Then I delete it

  @costprice
  Scenario: write the standard price in order to trigger the cost price / margin update
    Given I write the current standard price on products to update the stored function fields

  Scenario: update application version
    Given I set the version of the instance to "1.0.3"
