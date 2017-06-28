QoQa Products
=============

Customizations of the products:

* Add fields related to wine and liquors, used by ``wine_ch_report``
* Depends on ``product_brand`` so we have a brand on products
* Allow to generate automatically the internal reference of variants
  using the attributes' values
* Add a wizard to generate a given subset of variants
Generation of internal reference
--------------------------------

A new ``base_default_code`` on the product template allows to define a prefix
for the default code of the variants.

The internal reference of the generated variants is:

``{base_default_code} - {value1} - {value2} - {value3} ...``

Where value1, value2 (etc.) are the variant values selected.
Example: ``REF - Red - M``.

A code can be set on attribute values to have shorter references.


Workflow to generate products with variants
-------------------------------------------

1. Creation of a product template
2. Fill-in of the base default code
3. Selection of the variant values
4. On creation, all the variants are generated or later use the variant generator
5. If attribute values must be modified, this is still possible but Odoo might
   delete or deactivate variants in the process
6. Once all is good, activate the export of the products on the QoQa shops
   (``connector_qoqa`` feature)
7. Changing the attribute values on the template is no longer possible, because
   it might remove products already exported! It is still possible to edit or
   create variants manually.
