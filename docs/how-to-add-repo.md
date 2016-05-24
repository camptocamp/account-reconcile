# How to add a new addons repository


External addons repositories such as the OCA ones are integrated in the project using git submodules.

To add a new one, you only have to add the submodule:

```
git submodule add git@github.com:OCA/sale-workflow.git odoo/external-src/sale-workflow
git add odoo/external-src/sale-workflow
git commit -m"..."
```

And to add it in the `addons_path` option of the [Odoo's configuration file template](../odoo/etc/openerp.cfg.tmpl).
