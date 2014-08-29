# -*- coding: utf-8 -*-
@upgrade_from_1.0.54 @qoqa

Feature: upgrade to 1.1.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name       |
      | qoqa_offer |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE procurement_order p
    SET offer_id = so.offer_id
    FROM sale_order_line sol, sale_order so
    WHERE sol.procurement_id = p.id
    AND so.id = sol.order_id
    AND so.offer_id IS NOT NULL
    AND p.offer_id IS NULL
    """

    Given I set the version of the instance to "1.1.0"
