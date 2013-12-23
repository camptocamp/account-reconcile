@upgrade_from_1.0.0 @qoqa

Feature: upgrade to 1.0.1

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                       |
      | connector_qoqa             |
      | account_compute_tax_amount |
    Then my modules should have been installed and models reloaded

  @qoqa_backend
  Scenario: Configure the QoQa backend
    Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And I set global property named "property_voucher_journal_id_ch" for model "qoqa.backend" and field "property_voucher_journal_id" for company with ref "scenario.qoqa_ch"
    And the property is related to model "account.journal" using column "name" and value "Règlement par Bon Cadeau"
    Given I am configuring the company with ref "scenario.qoqa_fr"
    And I set global property named "property_voucher_journal_id_fr" for model "qoqa.backend" and field "property_voucher_journal_id" for company with ref "scenario.qoqa_fr"
    And the property is related to model "account.journal" using column "name" and value "Règlement par Bon Cadeau"

  @product @taxes @default
  Scenario: I set the default values for the taxes on the products
    Given I load the data file "setup/ir.values.yml"
    # OpenERP sets a value by default a key which prevent the default
    # value to be applied! It absolutely needs a NULL, which we can't
    # set with the ORM...
    And I execute the SQL commands
    """
    UPDATE ir_values SET key2 = NULL WHERE id IN (
        SELECT res_id FROM ir_model_data
        WHERE module = 'scenario'
        AND name IN ('ir_values_product_taxes_ch',
                     'ir_values_product_taxes_fr',
                     'ir_values_product_taxes_holding',
                     'ir_values_product_supplier_taxes_ch',
                     'ir_values_product_supplier_taxes_fr',
                     'ir_values_product_supplier_taxes_holding',
                     'ir_values_template_taxes_ch',
                     'ir_values_template_taxes_fr',
                     'ir_values_template_taxes_holding',
                     'ir_values_template_supplier_taxes_ch',
                     'ir_values_template_supplier_taxes_fr',
                     'ir_values_template_supplier_taxes_holding')
    )
    """

  @taxes @ch
  Scenario Outline: rename taxes with "TTC"
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "account.tax" with name: <name>
    And having:
      | key         | value          |
      | description | <new_tax_code> |

    Examples: currencies
      | name                | new_tax_code |
      | TVA due a 2.5% (TR) | 2.5% TTC     |
      | TVA due a 3.8% (TS) | 3.8% TTC     |
      | TVA due a 8.0% (TN) | 8.0% TTC     |
      | TVA 0% exclue       | 0% excl. TTC |
      | TVA due a 7.6% (TN) | 7.6% TTC     |
      | TVA due a 3.6% (TN) | 3.6% TTC     |
      | TVA due a 2.4% (TN) | 2.4% TTC     |

  @taxes @fr
  Scenario Outline: rename taxes with "TTC"
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I find a "account.tax" with name: <name>
    And having:
      | key         | value          |
      | description | <new_tax_code> |

    Examples: currencies
      | name                        | new_tax_code |
      | TVA collectée (vente) 20,0% | 20.0 TTC     |
      | TVA collectée (vente) 7,0%  | 7.0 TTC      |
      | TVA collectée (vente) 10,0% | 10.0 TTC     |
      | TVA collectée (vente) 8,5%  | 8.5 TTC      |
      | TVA collectée (vente) 2,1%  | 2.1 TTC      |
      | TVA collectée (vente) 5,5%  | 5.5 TTC      |
      | TVA collectée (vente) 5,0%  | 5.0 TTC      |
      | TVA collectée (vente) 19,6% | 19.6 TTC     |

  Scenario: update application version
    Given I set the version of the instance to "1.0.1"
