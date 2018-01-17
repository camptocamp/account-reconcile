<!--
This file has been generated with 'invoke project.sync'.
Do not modify. Any manual change will be lost.
Please propose your modification on
https://github.com/camptocamp/odoo-template instead.
-->
# How to integrate an open pull request of an external repository

First, ensure that you have `git-aggregator`:

```python
pip install git-aggregator
```

External addons repositories such as the OCA ones are integrated in the project
using git submodules (see [How to add a new addon repository](./how-to-add-repo.md)).
When we need to integrate a pull request that is not yet merged in the base branch
of that external repository we want to use, we create a consolidated branch that
we push on the fork at github.com/camptocamp.

The list of all pending merges for a project is kept in `odoo/pending-merges.yaml`.
This file contains a section for each external repository with a list of pull request
to integrate. It is used to rebuild the consolidated branches at any moment using git-aggregator.

For each repository, we maintain a branch named
`merge-branch-<project-id>-master` (look in `odoo/pending-merges.yaml` for the
exact name) which must be updated by someone each time the pending merges
reference file has been modified.
When we finalize a release, we create a new branch
`pending-merge-<project-id>-<version>` to ensure we keep a stable branch.

You can also create a `pending-merge-<project-id>-<branch-name>` for particular
needs.

## Adding a new pending merge

Beware with pending merge branches. It is easy to override a previously pushed
branch and have a submodule referencing a commit that do no longer exist.

1. Edit `odoo/pending-merge.yaml` file, add your pull request number in a section,
   if the section does not exist, add it:

  ```yaml
  ./external-src/sale-workflow:
    remotes:
      oca: https://github.com/OCA/sale-workflow.git
      camptocamp: https://github.com/camptocamp/sale-workflow.git
    merges:
      - oca 9.0
      # comment explaining what the PR does (42 is the number of the PR)
      - oca refs/pull/42/head
    # you have to replace <project-id> here
    target: camptocamp merge-branch-<project-id>-master
  ```

2. Rebuild and push the consolidation branch for the modified branch:

  ```
  invoke submodule.merges odoo/external-src/sale-workflow
  ```

3. If there was no pending merge for that branch before, you have to edit the `.gitmodules` file,
   replacing the remote by the camptocamp's one and if a branch is specified it needs to be removed
   or changed :

   ```
    [submodule "odoo/external-src/sale-workflow"]
      path = odoo/external-src/sale-workflow
    -   url = git@github.com:OCA/sale-workflow.git
    +   url = git@github.com:camptocamp/sale-workflow.git
    -   branch = 10.0
    +   branch = merge-branch-<project id>-master
    ```

4. Commit the changes and create a pull request for the change

## Notes

1. We usually always want the same `target` name for all the repositories, so you can use
   YAML variables to write it only once, example:

   ```yaml
   ./external-src/bank-payment:
     ...
     target: &default_target camptocamp merge-branch-1151-master
   ./external-src/sale-workflow:
     ...
     target: *default_target
   ```

2. If you are working on another branch than `master`, you'll need to change the name of the branch in the target.

## Merging only one distinct commit (cherry-pick)

Sometimes you only want to merge one commit into the consolidated branch (after
merging pull requests or not). To do so you have to add a `shell_command_after` block
in the corresponding section. Here is an example :

  ```yaml
  ./external-src/enterprise:
    remotes:
      odoo: git@github.com:odoo/enterprise.git
      camptocamp: git@github.com:camptocamp/enterprise.git
    merges:
      - odoo <branch-name or initial commit>
    target: *default_target
    shell_command_after:
      # Commit from ? Doing what ?
      -  git am "$(git format-patch -1 6563606f066792682a16936f704d0bdf4bc8429f -o ../patches)"
  ```

In the previous example the commit numbered 6563606... is searched in all the remotes of the section,
then a patch file is made and apply to the consolidated branch.
A file containing the patch will be saved in the patches directory and needs to be added in the commit
of the project.
