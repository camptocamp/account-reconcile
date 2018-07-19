<!--
This file has been generated with 'invoke project.sync'.
Do not modify. Any manual change will be lost.
Please propose your modification on
https://github.com/camptocamp/odoo-template instead.
-->
# How to add a new addons repository

External addons repositories such as the OCA ones are integrated in
the project using git submodules.

To add a new one, you only have to add the submodule:

```
git submodule add -b 9.0 git@github.com:OCA/sale-workflow.git odoo/external-src/sale-workflow
git add odoo/external-src/sale-workflow
```

And to add it in the `ADDONS_PATH` environment variable of the
[Dockerfile](../odoo/Dockerfile). As the `Dockerfile` is modified, a rebuild is
required.

Then commit the new submodule

```
git add odoo/Dockerfile
git commit -m"..."
```

# How to update an already installed addon repository

**Warning:** This part of the documentation is valid only when you have no pending-merges
(see [How to integrate an open pull request of an external repository](./how-to-integrate-pull-request.md)).

In this explanation, we are taking for example the following situation:
- There is a submodule: `my_nice_submodule`
- `my_nice_submodule` points to a specific commit in the branch `11.0`
- 2 new commits have been added to it with 10 files updated
- we want to update `my_nice_submodule` with it

In short, updating a submodule means moving the commit reference to a new one.

With cli you want to take latest commits
```
cd odoo/external-src/my_nice_submodule
git checkout 11.0
git pull
```
Then you want to commit them
```
cd ..
git add .
git commit -m"..."
```

You can now push it to your fork and open a pull-request

**Nota Bene:**
When you have your pull-request opened on github, you should see github listing the update
of the submodule with 10 files updated. If you see directly the update of the files, it means
that the folder has been added directly to the main git repository instead of a submodule.
