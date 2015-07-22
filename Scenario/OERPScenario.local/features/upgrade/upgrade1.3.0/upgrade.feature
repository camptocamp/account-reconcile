# -*- coding: utf-8 -*-
@upgrade_from_1.2 @qoqa

Feature: upgrade to 1.3.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                                   |
      | l10n_ch                                                |
      | l10n_ch_bank                                           |
      | l10n_ch_base_bank                                      |
      | l10n_ch_dta                                            |
      | l10n_ch_dta_base_transaction_id                        |
      | l10n_ch_payment_slip                                   |
      | l10n_ch_payment_slip_account_statement_base_completion |
      | l10n_ch_payment_slip_base_transaction_id               |
      | l10n_ch_sepa                                           |
      | l10n_ch_zip                                            |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.3.0"
