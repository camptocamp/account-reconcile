.. :changelog:

.. Template:

.. 0.0.1 (2016-05-09)
.. ++++++++++++++++++

.. **Features and Improvements**

.. **Bugfixes**

.. **Build**

.. **Documentation**

Release History
---------------

latest (unreleased)
+++++++++++++++++++

**Features and Improvements**

* Migrate module ``picking_dispatch_group`` that creates dispatches grouped by
  products according to some rules

**Bugfixes**

* Claim sync: remove <pre> tags
* Fix an issue when creating a new sale order line or emptying the product field

* Offers sync: add id in the title (``[xxxx] name of the offer``)

**Build**

* Use Docker image odoo-project 1.2.1

**Documentation**

9.3.1 (2016-07-25)
++++++++++++++++++

**Bugfixes**

* Correct paths and refund description re-added correctly in invoice view


9.3.0 (2016-07-25)
++++++++++++++++++

**Data Migration**

* Modules are now set as 'uninstalled' before we run anthem to prevent a lot
  of warnings at the start of anthem (which imports 'openerp')
* Configure new delivery carrier mappings with the new QoQa package types
* Move account statement profiles to the configuration of the journals

**Features and Improvements**

* Implement cancellation of credit notes in the QoQa connector
* Remove QoQa Shipper Services
* Rename QoQa Shipper Rates to QoQa Shipper Fees
* QoQa Package types are now "delivery.carrier"
* First pass for migrating specific_fct (dispatch part still on hold)
* Forbid usage of attribute values with more than 25 chars. Historic values
  might still be longer but are not allowed to be used.
* QoQa users are no longer imported as companies, now Odoo 9 allows an
  individual to have addresses
* Allow to edit name, ref and barcode of variants inline in the tree view with
  a new menu
* Install the enterprise barcode addon
* Portage of module delivery_carrier_label_dispatch renamed to delivery_carrier_label_batch
  to add setup of carrier option from picking batch to all related pickings.

**Performance**

* Disable 'tracking' ('Record created' notification, ...) on product
  variants, the creation of hundreds of variants is near 2 times faster
  and we don't need those notifications

**Bugfixes**

* Imported addresses do no longer takes the address fields of their parent
* Fix an issue when opening mail.composer due to user defaults.

**Build**

* Activate job runner on Rancher stacks
* Use odoo-project image version 1.0.3
* Extend the server timeout of HAProxy on Rancher to 6h to align with the nginx
  option (we can have very long requests on Odoo!)

9.2.0 (2016-07-11)
++++++++++++++++++

**Features and Improvements**

* Connector: transfer QoQa's payment id to account move lines'
  ``transaction_ref``
* Migrate addon to create a purchase line for each variant of a template
* Validating invoices takes less time.
* Creating an invoice from a SO takes less time.
* Migrate Wine report addon
* Migrate addon to add a wizard to split products in multiples packs
* Migrate Swiss PP labels addon
* Migrate addon to select a logo per shop on postlogistics delivery labels
* Migrate Swiss PP labels addon
* Migrate addon to create payment in swiss format DTA

**Bugfixes**

* Analytic accounts : allow to "search more..." on SO
  (due to performance improvement)
* Record rules on account_payment_mode for multi company

**Build**

* Add pending-merge for ``purchase_discount`` so the addon is now installed
* Integrate with the new Docker image using anthem and marabunta for the migration
* Use docker-compose v2 file format

9.1.0 (2016-06-29)
++++++++++++++++++

First tagged version of the migration.
The code and data migration are far to be ready, but things become testable
now.

**Data Migration**

* Migrate Claims Sequences
* Migrate Sales Shop data to QoQa Shop
* Migrate product attributes and brand
* And a handful of other fixes to the data

**Features and Improvements**

* First working version of `connector_qoqa` for QoQa4. Still a few API calls
  missing and edges a bit rough but good enough for the first tests.
* Most of the CRM and Claims addons are migrated
* A lot of addons migrated

**Bugfixes**

* Slow accounting dashboard: had to override
  account.account_journal_dashboard methods to change a few
  ORM calls by direct SQL and to totally remove one slow computation (account
  balance) and the graphs
* Speed up loading of the product view, when counting number of sales and
  purchases, the fix is naive though and needs improvements (doesn't consider
  company_id and user_id rules)

**Build**

* Use camptocamp/postgresql:pg9.5-latest in the dev composition
* Travis builds the test server on Rancher with the latest image on each commit
* Added Rancher composition for the integration server

**Documentation**

* Added Docker and Rancher documentation
