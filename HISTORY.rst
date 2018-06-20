.. :changelog:

.. Template:

.. 0.0.1 (2016-05-09)
.. ++++++++++++++++++

.. **Data Migration**

.. **Features and Improvements**

.. **Bugfixes**

.. **Build**

.. **Documentation**

Release History
---------------

latest (unreleased)
+++++++++++++++++++

**Features and Improvements**

* BSQOQ-52: Add barcode attribute in product export
* BSQOQ-65: Add archive functionality to crm.claim.category, crm.team, mail.alias
* BSQOQ-66: Add qoqa.teams and its views
* BSQOQ-54: Do not regenerate existing carrier labels unless forced +
  Store generated carrier labels when using the print action
* BSQOQ-70: The "Update QoQa Offers" action now works totally in background, no
  longer blocks the UI
* BSQOQ-70: Improve performance of the "Update QoQa Offers" action when
  changing the accounts
* BSQOQ-70: When using "Update QoQa Offers" action to change the VAT, it will
  be faster if the taxes are already correct
* BSQOQ-44_update: add unpack buttons to stock pack operation form
* BSQOQ-67: Add kanban dashboard for crm.team
* BSQOQ-56: Add shipping address change API
* BSQOQ-51: Allow per-variant prices
* BSQOQ-77: Improve SAV Dashboard loading time

* BSQOQ-62: add script to unpack packages from several locations

**Bugfixes**

* BSQOQ-82: Return None if barcode is empty
* BSQOQ-84: Replace `sav_qoqa_resposible` to `__export__.res_groups_65` group.
  Remove `sav_qoqa_resposible` group.
* BSQOQ-88: Fix Claim Categories search by add active_test False context
  to `name` field in search view
* BSQOQ-78: Fix style overlap on PO Form view
* BSQOQ-89: SAV Dashboard corrections

* Apply Odoo fix for the bug dropping indexes and constraints during some upgrades
  (https://github.com/odoo/odoo/pull/25069)

**Build**

**Documentation**


9.45.1 (2018-06-11)
+++++++++++++++++++

Moved to 9.45.2


9.45.0 (2018-05-28)
+++++++++++++++++++

Moved to 9.45.1


9.44.1 (2018-06-06)
+++++++++++++++++++

**Features and Improvements**

* BSQOQ-74: Improve filters for empty locations
* BSQOQ-76: Do not send claim notifications when using "I take it" button or if user mail setting is `none`


9.44.0 (2018-04-27)
+++++++++++++++++++

**Features and Improvements**

* BSQOQ-49: Add filters for empty locations
* BSQOQ-45: replace Explanation and state with EAN in Batch picking report.
  fix report printing issue.
* BSQOQ-47: Manage responsible notifications on claim creation/update
* BSQOQ-44: Unpack of package now deletes the package and fills
  it's picking with products


9.43.2 (2018-04-25)
+++++++++++++++++++

**Bugfixes**

* BSQOQ-34: Send QoQa Ids to the API instead of the binding records ids
* BSQOQ-34: Fix call to disable_modifications api (PUT instead of POST + change to JSON content)


9.43.1 (2018-04-17)
+++++++++++++++++++

**Bugfixes**

* BSQOQ-43: API returns a "missing_error" if the address doesn't exist instead of "user_error"


9.43.0 (2018-03-27)
+++++++++++++++++++

**Features and Improvements**

* BSQOQ-43: Add controller for disabling an address
* BSQOQ-34: Add controller for changing the shipping addresses of sale orders
* BSQOQ-34: Add job to disable change of shipping address on sale orders
* BSQOQ-40: Batch print of carrier delivery labels
* Include patch https://github.com/OCA/connector/pull/270 to prevent job runner
  to create one anonymous session for each executed job, which puts a lot of
  pressure on Redis


9.42.0 (2018-03-07)
+++++++++++++++++++

**Features and Improvements**

* BIZ-898: Set job priority to 40
* BIZ-1337: Propagate internal reference on product variant
* BIZ-1342: Add Total Quantity to PO and pdf report

**Bugfixes**

* BSQOQ-36: Don't cancel refund when using qoqa_offer_update

**Build**

* Upgrade nginx to 9.0-1.2.1


9.41.2 (2018-02-07)
+++++++++++++++++++

**Bugfixes**

* BIZ-747 : Missing recompute taxes
* BSQOQ-27: S3 import indexError


9.41.1 (2018-02-06)
+++++++++++++++++++

**Features and Improvements**

* BIZ-747 : Wizard to modify VAT and Account on offer

**Bugfixes**

* Reactivate import of discounting issuances for promo, but not for vouchers (BIZ-1248)
* BIZ-403: Filtre SAV
* BIZ-1266: Fix Check of property rules
* Add some indices used in slow queries

**Build**

* BIZ-1093: Update odoo-cloud-platform


9.40.4 (2018-01-09)
+++++++++++++++++++

**Bugfixes**

* BIZ-1109: fix mass reconcile run several times on the same account


9.40.3 (2018-01-08)
+++++++++++++++++++

**Bugfixes**

* BIZ-478 : fix Double authentification QR-code generation for user with special chars


9.40.2 (2017-12-22)
+++++++++++++++++++

**Features and Improvements**

* BIZ-1020: execute automatic mass reconciliation as asynchronous jobs
* BIZ-1020: disable cash basis which improves a lot the time required to reconcile


9.40.1 (2017-12-21)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* BIZ-895: update connector import for new VAT
* BIZ-1020: apply some optimizations during automatic mass reconciliation

**Build**

**Documentation**

* BIZ-902: Update local doc and add base for aws commands

9.40.0 (2017-12-14)
+++++++++++++++++++

**Features and Improvements**

* BIZ-895:

  * Install module account_fiscal_position_rule
  * Install module account_fiscal_position_rule_purchase
  * Install module account_fiscal_position_rule_sale

**Bugfixes**

* BSQOQ-35: Fix qoqa_offer_update invoice with total at 0.0

**Build**

**Documentation**


9.39.0 (2017-12-11)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* BIZ-425 Labels with unsorted tracking numbers

**Build**

**Documentation**


9.38.2 (2017-12-07)
+++++++++++++++++++

**Features and Improvements**

* New addon sale_automatic_workflow_split, split the automatic workflows in
  several independent crons (no card, following performance issues on
  production). Allow different intervals. Validating invoices takes a lot of
  time for instance but does not need to be done very fast. Confirming sales
  orders has to wait on validation on invoices, but we want this operation to
  be fast.


9.38.1 (2017-11-30)
+++++++++++++++++++

**Bugfixes**

* BIZ-946 Fix voucher calculation


9.38.0 (2017-11-29)
+++++++++++++++++++

**Features and Improvements**

* BIZ-878: Make cancellation of sales orders only synchronous
* Changes Sales button on claim to include inactive SO
* BIZ-736 add scenario to modify locations' partners
* BIZ-711 BIZ-712 Remove discount import from connector_qoqa
* BIZ-711 BIZ-712 Remove import of voucher issuances from connector_qoqa
* BIZ-711 BIZ-712 Import vouchers as negative line in sales orders

**Build**

* After multiple fixes, steps of 9.37.0 and 9.37.1 have been moved to 9.38.0
     in order to have a clean release while putting it in production


9.37.1 (2017-11-21)
+++++++++++++++++++

**Features and Improvements**


**Bugfixes**

* BIZ-712 fix missing git add on last PR
     voucher sould be removed for generic binders as we created a dedicatred one
* BIZ-425 preparation label must be ordered by tracking number
* BIZ-736 Allow to use location's partner for product return
* BIZ-478 only admin can edit field mfa_enable to de/activate double auth


**Build**

**Documentation**


9.37.0 (2017-11-15)
+++++++++++++++++++

**Features and Improvements**

* BIZ-677 Improve stock.picking & SO/quot tree views
* Add "TWINT" in the list of partners imported from the CAMT.053 file
* BSQOQ-22: Add Unclaimed Package Delivery as action on claim tree view
* BSQOQ-24: Claim UI improvements

  * Form - Remove useless column on product returns o2m
  * Form - Add sale count and claims smart button in place of purchase
  * Form - Add picking out smart button
  * Tree and Form - Add buttons to link to backoffice
  * Form - Add a button "I take it!" to assign current user
  * Tree - Add an action "I take it!" to assign current user in "Action" menu
  * Tree - Add line colors depending on last_message_date and state
  * Search - filter on products of claim lines
  * Picking Form - Always display initial demand in pickings - make it readonly instead of invisible
  * Add warranty info on claim.line instructions and return address
  * Add partner tags field on claim
  * Add crm stage "Return received"
  * Filter category field by sale team

* Allows a giftcard to be used on many QoQa sale order in QoQa connector BIZ-712

**Bugfixes**

* Map the payment_id on discount accounting group instead of payment voucher
* Restore possibility to run connector_qoqa tests with pytest
* Pass qoqa_shop_id when creating claim from wizard Unclaimed Package Return

**Build**

* Upgrade Dockerimage to 9.0-2.4.1

**Documentation**


9.36.0 (2017-11-06)
+++++++++++++++++++

**Features and Improvements**

* Install auth_totp
* BIZ-711 improve reconciliation of future sales of gift cards

**Bugfixes**

* Fix BIZ-709 on the change quantity wizard
  that does not manage the use case of a template witout active variant

**Bugfixes**

**Build**

**Documentation**

9.35.0 (2017-10-17)
+++++++++++++++++++

**Features and Improvements**

* Add unreserve all BIZ-714

**Bugfixes**

**Build**

**Documentation**


9.34.1 (2017-10-17)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* fix crm.claim TODO filter installation
* Fix date in voucher BIZ-649

**Build**

**Documentation**


9.34.0 (2017-10-10)
+++++++++++++++++++

**Features and Improvements**

* Uninstall password security
* Transform crm.claim TODO filter into if.filter

**Bugfixes**

**Build**

**Documentation**


9.33.0 (2017-09-21)
+++++++++++++++++++

**Features and Improvements**

* Harden qoqa mail message to be resilient to faulty call to message_post BIZ-27
* Installing account_invoice_update_wizard to allows edition of some fields of confirmed invoices  BIZ-243
* Add custom time filter on CRM claim BIZ 403
* Install password security addon BIZ-476
* Add TWINT configuration BIZ-501


**Bugfixes**

**Build**

**Documentation**


9.32.1 (2017-08-31)
+++++++++++++++++++

**Features and Improvements**

* Hot fix reverting support of biz 27 for crm.claim

**Bugfixes**

**Build**

**Documentation**


9.32.0 (2017-08-28)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* Validation of refund takes 1.5 seconds instead of 15
* Make the inactive/delete action of a product more robust:
  - do not try to delete a product on the API if we have no qoqa id
  - ignore error raised by the API when it doesn't know the product, goal being
    to delete it, if it doesn't exist our goal is reached


**Build**

**Documentation**


9.31.2 (2017-08-16)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* Hot Fix of batch picking report

**Build**

**Documentation**


9.31.1 (2017-08-10)
+++++++++++++++++++

**Features and Improvements**

**Bugfixes**
Fix merge error in batch_picking_report

**Build**

**Documentation**


9.31.0 (2017-08-09)
+++++++++++++++++++

**Features and Improvements**
* Imporve batch_picking_group order and add separation page, biz 232
* Remove pending merge in account payment

**Bugfixes**

* Fix QoQa mail message en crm.claim, biz 27

**Build**

**Documentation**


9.30.0 (2017-07-27)
+++++++++++++++++++

**Features and Improvements**

* When the authentication to Q4 API fails, shows the error message returned by the API
* Delete product and variants on QoQa API when product is disabled on Odoo (BSQOQ-6)
* Restrict the deletion of a payment order and allow his cancellation
* ADD conditional "View in Odoo" link in mail message https://jira.camptocamp.com/browse/BIZ-27
* Adaptation of cancellation of orders with service only BSQOQ-4
* Add pagebreak per stock location and preparation report
* Add search on name of supplier invoice
* Allow cancelling of Payment Order

**Bugfixes**
* Fix mass reconcile : Check the write-off limit when dealing with a partial reconcile invoice
* Add analytic account on mass reconcile rules
* Show supplier invoice name, in order to set the supplier invoice reference on invoice
* Allow to auto-assign claim
* Correction of balance in move line for reporting
* Script to correct taxes on invoices and related sale order
* Script to correct Quants
**Build**
* Use camptocamp/odoo-project:9.0-2.3.0

**Documentation**


9.29.0 (2017-07-12)
+++++++++++++++++++

**Features and Improvements**

* BIZ-898: Installation module

**Bugfixes**

**Build**

**Documentation**


9.28.0 (2017-06-22)
+++++++++++++++++++

**Features and Improvements**

* Improve performance for invoice validation and batch picking display
* Install module product_variant_exclusion
* Improve report batch picking (dispay picking comment)
* Improve mass reconcile avoid collision between jobs
* Uninstall modules installed by mistake
* Improve stock performance with index

**Bugfixes**

**Build**

**Documentation**


9.27.2 (2017-06-09)
+++++++++++++++++++

**Bugfixes**

* Forbid partial transfer of batch pickings (BIZ-117)



9.27.1 (2017-06-06)
+++++++++++++++++++

**Features and Improvements**

* Don't add email in claim body


9.27.0 (2017-05-30)
+++++++++++++++++++

**Features and Improvements**

* Fix stock levels and stock locations after migration
* Set shipping address in PO
* Fix reconcile cron order
* Remove default check boxes in "Check Availability" wizard


9.26.1 (2017-05-24)
+++++++++++++++++++

**Features and Improvements**

* Display product information on batch report lines


9.26.0 (2017-05-17)
+++++++++++++++++++

**Bugfixes**

* Fix problem with complete_name on stock locations
* Add new "Tous les stocks" location to only get stock info from it
* Re-use original package in return for unclaimed claims
* Correct workflows for IN/OUT from claims (unclaimed or not)
* Fix Swiss PP PDF label formatting
* Use correct field name for delivery date


9.25.0 (2017-05-08)
+++++++++++++++++++

**Features and Improvements**

* Hide "Create Variants" button when editing variant
* Remove action_assign for pickings created from claims
* When a picking operation contains a pack instead of a product, we can
  now include it in a batch picking as well.
* Allow to print labels on packs without products (return of pack for instance)

**Bugfixes**

* Do not change status when an internal note is done on a claim
* Fix invoice creation from a claim
* Final fixes for claim mails
* Create default price rules for delivery carriers
* Fix related action button for export tracking jobs
* Fix generation of labels when there is more than one pack per picking
* Use correct field to generate Swiss PP labels


9.24.13 (2017-05-09)
++++++++++++++++++++

**Features and Improvements**

* Change S3 configuration


9.24.12 (2017-05-04)
++++++++++++++++++++

**Features and Improvements**

**Bugfixes**

* Use pack_operation_product_ids for tracking export

**Build**

**Documentation**


9.24.11 (2017-05-04)
++++++++++++++++++++


9.24.10 (2017-05-04)
++++++++++++++++++++


9.24.9 (2017-05-04)
+++++++++++++++++++

**Bugfixes**

* Revert "deactivate mail when newly subscribed to a claim" (more issues)


9.24.8 (2017-05-04)
+++++++++++++++++++

**Bugfixes**

* Add claim number in call to Pay by email.
* Deactivate mail when newly subscribed to a claim


9.24.7 (2017-05-03)
+++++++++++++++++++

**Bugfixes**

* Block on-change (force wizard) on batch carrier change
* Fix loop so that mail_signature is correctly set in claim
* Fix invoice generation for unclaimed delivery
* Correct server action + filter on sent e-mails


9.24.6 (2017-05-01)
+++++++++++++++++++

**Features and Improvements**

* Modify S3 import parameters

**Bugfixes**

* Add pick/pack info to all batch label exceptions


9.24.5 (2017-05-01)
+++++++++++++++++++

**Bugfixes**

* Add pick/pack info to all batch label exceptions


9.24.4 (2017-05-01)
+++++++++++++++++++

**Features and Improvements**

* Allow to configure Q4 API URL with environment variables

**Bugfixes**

* Fix empty PDF on batch labels


9.24.3 (2017-05-01)
+++++++++++++++++++

**Bugfixes**

* Fix onchange for batch pickings


9.24.2 (2017-04-29)
+++++++++++++++++++

**Bugfixes**

* Delay jobs when the API is in maintenance mode

**Build**

**Documentation**
* Disable automatic creation of order line for shipping costs for
  invoices on delivery.
* Change Q4 api URL



9.24.1 (2017-04-29)
+++++++++++++++++++

**Features and Improvements**

* Cloud platform: do not require metrics on production

**Bugfixes**

* Disable automatic creation of order line for shipping costs for
  invoices on delivery.


9.24.0 (2017-04-27)
+++++++++++++++++++

**Features and Improvements**

* Add taxes for display in account move view
* Optimize main views with indices
* Add plain text version of claim description to quote in mails

**Bugfixes**

* Correctly translate / set mail signatures in shops
* Remove default timeout of 120 seconds on attachment script
* Send correct tracking number to connector
* Correct price on carrier products to have the correct fixed price


9.23.0 (2017-04-19)
+++++++++++++++++++

**Data Migration**

* Add a script to move back S3 small files to DB
* Increase mail cleanup delay for migration

**Features and Improvements**

* Change parameters in SEPA payment modes
* Add return instructions on claim lines
* Add indexes on frequenty used fields to improve performance
* Improve check_assign_all cron performance

**Bugfixes**

* Use carrier's price instead of the one set in picking for unclaimed


9.22.0 (2017-04-07)
+++++++++++++++++++

**Data Migration**

* Deactivate crons
* Add more claim category mappings

**Features and Improvements**

* Set attribut codes per template

**Build**

* Remove old rancher config


9.21.0 (2017-04-04)
+++++++++++++++++++

**Data Migration**

* Add special case to set default out picking type
* Set attachment bucket name according to running env

**Features and Improvements**

* Add module stock_picking_operation_quick_change

**Bugfixes**

* Use correct IDs for refund if coming from claim


9.20.0 (2017-03-27)
+++++++++++++++++++

**Data Migration**

* Migrate attachment URLs to S3

**Features and Improvements**

* Update account types

**Bugfixes**

* Issue with description_id when cancelling sale order
* Correct reconciliation type to replace "bank.statement"
* Do not fail script is postgres is not superuser


9.19.0 (2017-03-08)
+++++++++++++++++++

**Data Migration**

* Correctly migrate promo / voucher accounting issuances
* Configure currency rate update process
* Update all branches
* Fix issues with non-migrated res.bank IDs

**Features and Improvements**

* Add EAN13 to PO report lines
* Ported from 7.0 : use refund description in refund wizard
* Specific changes on claims:
  * move "Category" to claim header
  * "warranty_return_partner" in list view for claim lines
  * check line warranty at creation
  * change description type to HTML
* Hide "General Ledger" menus

**Bugfixes**

* Split in packs was splitting only the operations of the first picking

**Build**

**Documentation**


9.18.0 (2017-02-07)
+++++++++++++++++++

**Data Migration**

* Correctly set default values in "is_wine" and "is_liquor" on product
templates.
* Add step to shift QoQa IDs for promo issuances

**Features and Improvements**

* Add product category name in connector
* Hide unwanted menus / reports in accounting and stock
* Order move lines in reverse chronological order

**Bugfixes**

* Correct formatting of CSCV wine report
* Only set Swiss crons as active and fix "SAV" location translation
* PO download name now correctly set


9.17.0 (2017-01-23)
+++++++++++++++++++

**Data Migration**

* Configure tax codes (tags)

**Features and Improvements**

* Improve speed of split pack operations
* Show transaction ref on account move line tree views
* Add an option in automatic workflows to set sales orders to done when fully
  delivered and invoiced
* Add 7.0 code to add onchange of account depending on taxes in product
* Add 7.0 code to change timeout for call to Postlogistics web service
* Correct tracking number in batch picking report
* Add validator back in PO

**Bugfixes**

* Send a confirmation email when a claim is created from the connector
* Settle payment id instead of order id
* Get the total amount paid when several payment methods are used (payment +
  voucher).  This total is used to check if the order has been totally paid so
  it must include all the payments.


9.16.0 (2016-12-13)
+++++++++++++++++++

**Features and Improvements**

* Connector: import payments made with vouchers as move lines
* Update stock-logistics-workflow

**Bugfixes**

* Correct filename for batch picking delivery labels
* Fix issues with wine reports (boolean not set, error in template)


9.15.0 (2016-11-30)
+++++++++++++++++++

**Bugfixes**

* Correct filename for batch picking delivery labels


9.14.0 (2016-11-29)
+++++++++++++++++++

**Data Migration**

**Features and Improvements**

* Clean default values for SMTP mail servers
* Fix address display in reports
* Add accounting group to new "Payments" group

**Bugfixes**

* Fix scheduler methods calls in connector_qoqa
* Send both attribute and attribute positions in product exports
* Price unit now displayed correctly in PO report


9.13.0 (2016-11-17)
+++++++++++++++++++

**Data Migration**

* Set correct type on account 29910 and add 3 purchase journals for currencies
* Migrate stock journals to picking types, more fine-grained, with In, Out, Internal
* Fix stock location names again
* Map claim categories

**Features and Improvements**

* Add IN and OUT picking types for unclaimed claims
* Export position of attributes values instead of attributes on variant export

**Bugfixes**

* Do not cancel invoices when the cancellation of the sale is not done during
  the day (MIGO-344)


9.12.0 (2016-11-01)
+++++++++++++++++++

**Data Migration**

* Delete 3 more taxes
* Correctly migrate display_name for offers
* Correct banks on journals

**Bugfixes**

* Fix translation for field "Customer Satisfaction" in claims
* Remove "Loutres" as automatic follower on all claims
* Correct addresses in reports + migrated columns in PO report


9.11.0 (2016-10-26)
+++++++++++++++++++

**Data Migration**

* Migrate stock journals to picking types

**Features and Improvements**

* Add a sales exception: paid amount on QoQa should match total amount
* Synchronize shipping fees from QoQa (MIGO-354)
* Migrate stock journals to picking types
* Set server actions as writable (needed to update code)
* Clean taxes
* Update odoo-monitoring branch
* CAMT.053: Fill partner id and label depending on free text

**Bugfixes**

* Remove "vendor" translation for supplier stock location
* Store offer display_name to be searchable/orderable
* Add translated field name for Customer Satisfaction on claims


9.10.0 (2016-10-06)
+++++++++++++++++++

**Data Migration**

* Remove the [xxxx] prefix from qoqa offers (now added in name_get)
* Migrate done and cancel picking dispatchs (MIGO-384)
* Add refund parameters to payment method migration
* Remove users from hidden menus
* Set default currency exchange journal
* Migrate reconciliation rules

**Features and Improvements**

* Show delivery button on sales orders even when all is delivered (MIGO-346)
* Allow to search offers by code
* Better error messages for errors occurring on the QoQa4 API (MIGO-345)
* Synchronize position of product attributes
* Remove Odoo header in e-mails

**Bugfixes**

* Several fixes on the cancellation on sales orders (MIGO-344)
* Fix errors related to bindings being inactive
* Correct tracking number url button never shown on packages
* Correct sender for emails from claims
* Use PostFinance additional text as entry name
* Correct action for mail template
* Use advanced_ref instead of bank_statement rule
* Change test due to change in message type
* Correct claim status only on outgoing e-mails

**Build**

* Install ``specific_report``
* Use a pending-merge branch for l10n-switzerland


9.9.0 (2016-09-20)
++++++++++++++++++

**Data Migration**

* Empty company on products, all products should now be shared (MIGO-328)
* Activate migrated batch pickings
* Cancel french draft invoices (MIGO-334)
* Require analytic account on Income, Other incomes, cost of revenue account
  types (MIGO-322)

**Features and Improvements**

* Allow to select delivery method even on IN pickings (MIGO-330)
* Import order reference from QoQa4 (MIGO-307)

**Bugfixes**

* Allow partner delivery address to be non-mandatory
* Export refund even if the origin sales order is inactive (MIGO-344)
* On export of refund, we now store back the payment id, not the
  'transaction_id' field (MIGO-332)
* Rework cancellation of sales orders, invoices were not cancelled (MIGO-348)
* Errors on picking labels, mainly due to fields renamed

**Build**

* Add pending merge in carrier-delivery for a new fix


9.8.0 (2016-09-12)
++++++++++++++++++

**Data Migration**

* Prefix the old sale order lines qoqa ids, because we do no longer use the
  same object on qoqa4 for the ids
* Reset the purchase mail template because it was referring to removed fields
  (MIGO-292)

**Features and Improvements**

* optimized version of the financial QWeb reports
* Send sequence of the attributes on exported product variants (MIGO-321)
* Add an action on the products to generate purchases orders from the
  orderpoints (MIGO-326)

**Bugfixes**

* use journal debit account on invoice with specific payment modes
* look for quants in top-level packages (issue with RMA product return)
* problems on move import (invalid error message, wrong debit amount)
* Set sales orders analytic account on modification of the QoQa shop and when
  importing them (MIGO-322)
* Allow to have no shipping fee in imported orders
* Wrong quantity in imported sale order lines when the lot size is above 1
  (MIGO-329)
* Fix sale automatic working not working because the filters used for the
  workflows were restricted to the admin user, where we run the automatic cron
  with other users (CH, FR)
* Fix cancellation on sales orders not possible when an invoice already exist
  (MIGO-320)
* Fix 23 sales orders buggy since V7 as they are 'to invoice' but not invoiceable.
* Fix error when trying to cancel a refund without transaction id (MIGO-332)

**Build**

* Update connector-ecommerce pending merge branch


9.7.1 (2016-09-05)
++++++++++++++++++

**Build**

* Update the server-tools pending merge branch for a correction in mail_cleanup


9.7.0 (2016-09-05)
++++++++++++++++++

**Data Migration**

* Again a correction on the locations complete name
* Configure unclaimed ids

**Bugfixes**

* Configure 'web.base.url' to print reports correctly
* Corrections in claims regarding stock locations
* Reference on supplier invoice is now required [MIG-287]

**Build**

* The 'release.bump' task adds the entry in 'migration.yml' if it does not
  exist
* Switch back to the api-staging
* Add a new module that logs requests, that will be used to do usage analysis /
  monitor the duration of the requests.


9.6.1 (2016-08-30)
++++++++++++++++++

**Build**

* Change integration connector API url to api-sprint which have more recent
  fixes


9.6.0 (2016-08-30)
++++++++++++++++++

**Data Migration**

* Set the correct unclaimed categories on the company
* Initialize a domain on QoQa shops used to generate the offers links
* Delete custom filters (they refer to a modified data model)

**Features and Improvements**

* Adapt the offers edition link to the new URL
* Add a menu to edit the QoQa shops
* Prevent to remove an exported variant

**Bugfixes**

* Addresses imported in orders are copied to new addresses. Now they are
  imported as inactive.

**Documentation**

* Document upgrade scripts


9.5.0 (2016-08-29)
++++++++++++++++++

**Data Migration**

* Remove custom views (dashboards), as the original views have been updated, it
  is better to let the users create them again
* Correct stock location complete names, again (some were still wrong)
* Change mapping of ``qoqa_id`` on shops (modified on the backend)
* Configure journal and payment modes

**Features and Improvements**

* Add a button on the product templates to open the editable tree view of the
  variants
* Implement the new pay by email url
* Improvements on claims:
  * Set the team from the claim category if there is no default value in the
    mail alias
  * Add the original description in the quoted message when sending a new message
  * Import the claim category
  * Write more information in the imported claim's description (category, ...)

**Bugfixes**

* Fix variants editable tree view; barcode and brand fields on variants tree
  view
* Fix the custom filters of the wine moves analysis view
* Fix computation of partner display name which made the partner not searchable
* The display name of partners do no longer show weird ', , ' when there is no
  address
* Fix creation of delivery method
* Import of job for canceled orders do no longer fail
* Fix import of orders failing due to a renaming in the API (`unit_price` →
  `lot_price`)
* Add missing access rights on qoqa.crm.claim
* Fix error when saving a claim which has no responsible

**Build**

* Add an ``invoke`` task to push the pending-merges branches


9.4.0 (2016-08-22)
++++++++++++++++++

**Data Migration**

* Setup the accounting journals, completion rules, s3 imports
* Migration of picking dispatchs
* Correct stock location complete names

**Features and Improvements**

* Migrate module ``picking_dispatch_group`` that creates dispatches grouped by
  products according to some rules
* Migration of default shipping labels
* Migration of specific purchase report
* Migration of specific invoice report
* Port 7.0 feature: default claim category

**Bugfixes**

* Claim sync: remove <pre> tags
* Fix an issue when creating a new sale order line or emptying the product field
* Offers sync: add id in the title (``[xxxx] name of the offer``)
* Fix responsive design on the claim views
* Fix security rules on employees

**Build**

* Use Docker image odoo-project 1.3.0
* Add invoke with a ``bump`` task to increment the release number

**Documentation**

* Use tar.gz instead of tar for backups of volumes

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
