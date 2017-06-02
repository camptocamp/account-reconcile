<!--
This file has been generated with 'invoke project.sync'.
Do not modify. Any manual change will be lost.
-->
# How to integrate an open pull request of an external repository

First, ensure that you have `git-aggregator`:

```python
pip install git-aggregator
```

External addons repositories such as the OCA ones are integrated in the project
using git submodules.  When we need to integrate a pull request that is not yet
merged in the base branch, we create a consolidated branch that we push on the fork
github.com/camptocamp.

In `odoo/pending-merges.yaml`, we keep the list of all the pending merges we
need, so we can rebuild the branch at any moment.

For each repository, we maintain a branch named
`pending-merge-<project-id>-master` (look in `odoo/pending-merges.yaml` for the
exact name)  which must be updated by someone when we modify the pending merges
reference file.  When we finalize a release, we create a new branch
`pending-merge-<project-id>-<version>` to ensure we have a stable branch.

You can also create a `pending-merge-<project-id>-<branch-name>` for particular
needs.

## Adding a new pending merge

We work on `master` for adding a new pending-merge, we don't use a pull
request. The reason is that we override the existing pending-merge branch when
we rebuild it, so if we don't push the update of the submodule on master, we
break the other devs' submodules (they will refer to a commit that no longer exist).


1. edit `odoo/pending-merge.yaml` file, add your pull request number in a section,
   if the section does not exist, add it:

  ```yaml
  ./external-src/sale-workflow:
    remotes:
      oca: https://github.com/OCA/sale-workflow.git
      camptocamp: https://github.com/camptocamp/sale-workflow.git
    merges:
      - oca 9.0
      # comment explaining what the PR does (42 is the number of the PR
      - oca refs/pull/42/head
    # you have to replace <project-id> here
    target: camptocamp merge-branch-<project-id>-master
  ```

2. rebuild and push the consolidation branch for the modified branch:

  ```
  cd odoo
  gitaggregate -c pending-merges.yaml -d "./external-src/sale-workflow" -p
  ```

3. If there was no pending merge for that branch before, you have to edit the `.gitmodules` file
   and replace the remote by the camptocamp's one

   ```
    [submodule "odoo/external-src/sale-workflow"]
      path = odoo/external-src/sale-workflow
    -   url = git@github.com:OCA/sale-workflow.git
    +   url = git@github.com:camptocamp/sale-workflow.git
    ```

4. commit the git submodule change and push it on the `master` branch

Note: we usually always want the same `target` name for all the repositories, so you can use
YAML variables to write it only once, example:

```yaml
./external-src/bank-payment:
  ...
  target: &default_target camptocamp merge-branch-1151-master
./external-src/sale-workflow:
  ...
  target: *default_target
```

Note: If you are working on another branch than `master`, you'll want to use a
different name for the consolidation branch (the name of the consolidation
branch is the `target` attribute in `pending-merges.yaml`).
