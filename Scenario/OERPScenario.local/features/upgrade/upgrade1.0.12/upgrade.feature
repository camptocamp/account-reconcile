# -*- coding: utf-8 -*-
@upgrade_from_1.0.11 @qoqa

Feature: upgrade to 1.0.12

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | qoqa_offer                                             |
      | connector_qoqa                                         |
    Then my modules should have been installed and models reloaded

  Scenario: copy partners languages to their addresses
    Given I execute the SQL commands
    """
    UPDATE res_partner addr
    SET lang = p.lang
    FROM res_partner p
    WHERE p.id = addr.parent_id
    AND addr.lang <> p.lang
    AND p.lang IS NOT NULL
    """

  @offerprice
  Scenario: fix prices of offers
    Given I import again from QoQa the offer position with a missing lot price

  Scenario: update application version
    Given I set the version of the instance to "1.0.12"
