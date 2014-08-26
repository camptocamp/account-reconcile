# -*- coding: utf-8 -*-
@upgrade_from_1.0.5 @qoqa

Feature: upgrade to 1.0.6

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | l10n_ch_payment_slip_base_transaction_id               |
      | l10n_ch_payment_slip_account_statement_base_completion |
      | l10n_ch_dta_base_transaction_id                        |
    Then my modules should have been installed and models reloaded

  @mail_setup_incoming
  Scenario: Confirm the incoming mail server
    Given I need a "fetchmail.server" with oid: scenario.openerp_catchall
    And having:
    | name | value            |
    | name | openerp_catchall |
    And I test and confirm the incomming mail server

  Scenario: update application version
    Given I set the version of the instance to "1.0.6"
