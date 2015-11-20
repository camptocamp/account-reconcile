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
    Then my modules should have been installed and models reloaded

  Scenario: change all journal to allow cancelling
    Given I execute the SQL commands
    """
    UPDATE account_journal set update_posted = 't';
    """
  Scenario: upgrade application version
    Given I set the version of the instance to "1.4.0"
