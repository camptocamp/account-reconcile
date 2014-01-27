# -*- coding: utf-8 -*-
@upgrade_from_1.0.4 @qoqa

Feature: upgrade to 1.0.5

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                 |
      | connector_qoqa                       |
      | l10n_ch_base_transaction_id          |
      | account_invoice_reference |
      | account_advanced_reconcile_transaction_ref |
      | account_statement_transactionid_completion |
      | base_transaction_id |
    Then my modules should have been installed and models reloaded

  Scenario: set invoices inactive because the field was missing when they have been imported
    Given I execute the SQL commands
    """
    UPDATE account_invoice SET active = false WHERE id IN (
      SELECT invoice_id FROM sale_order_invoice_rel rel
      INNER JOIN sale_order so
      ON so.id = rel.order_id
      WHERE so.active = false
    );
    """

  Scenario: update application version
    Given I set the version of the instance to "1.0.5"
