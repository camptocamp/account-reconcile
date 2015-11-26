# -*- coding: utf-8 -*-
@upgrade_from_1.3.9 @qoqa

Feature: upgrade to 1.4.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

    Given I update the module list

    Given I uninstall the following modules
      | name                       |
      | account_default_draft_move |

    Given I install the required modules with dependencies:
      | name                 |
      | account_move_locking |
      | account_cancel       |
      | specific_fct         |
    Then my modules should have been installed and models reloaded

  Scenario: change all journal to allow cancelling
    Given I execute the SQL commands
    """
    UPDATE account_journal set update_posted = 't';
    """
  Scenario: Validate all moves
    Given I need to validate all moves from "01-01-2015" to "12-31-2015" on company "QoQa Services SA"

  Scenario: change automatic workflow
    Given I need a "sale.workflow.process" with oid: sale_automatic_workflow.automatic_validation
    And having:
    | name              | value            |
    | invoice_quantity  | order            |
    | create_invoice_on | on_order_confirm |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.4.0"
