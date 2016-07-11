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

**Data Migration**

**Features and Improvements**

**Bugfixes**

**Build**

**Documentation**

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
