# -*- coding: utf-8 -*-
@upgrade_from_1.0.28 @qoqa

Feature: upgrade to 1.0.29

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

  Scenario: Set all the new claim to draft to avoid to send emails on already created claims
    Given I execute the SQL commands
    """
    UPDATE crm_claim SET stage_id = 2, state = 'open' WHERE state = 'draft';
    """

  Scenario: upgrade
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                                   |
      | specific_fct                                           |
      | crm_claim_merge                                        |
      | crm_claim_mail                                         |
      | web_confirm_window_close                               |
      | web_send_message_popup                                 |
    Then my modules should have been installed and models reloaded

  Scenario: Set the Re-Open Claim server action on the mail incoming servers
    Given I find a "fetchmail.server" with oid: scenario.openerp_catchall
    And having:
      | name      | value                               |
      | action_id | by oid: crm_claim_mail.reopen_claim |
    Given I find a "fetchmail.server" with oid: scenario.openerp_incomming_claim
    And having:
      | name      | value                               |
      | action_id | by oid: crm_claim_mail.reopen_claim |

  Scenario: update application version
    Given I set the version of the instance to "1.0.29"
