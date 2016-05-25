# How to integrate an open pull request of an external repository

First, ensure that you have `git-aggregator`:

```python
pip install git-aggregator
```

## Proposing a new pending merge

External addons repositories such as the OCA ones are integrated in the project
using git submodules.  When we need to integrate a pull request that is not yet
merged in the base branch, we create a consolidated branch that we push on
github.com/camptocamp.

In `odoo/pending-merges.yml`, we keep the list of all the pending merges we need.

For each repository, we maintain a branch named
`pending-merge-<project-id>-master` (look in `odoo/pending-merges.yml` for the
exact name)  which is updated when we modify the pending merges reference file
on master.  When we finalize a release, we create a new branch
`pending-merge-<project-id>-<version>` to ensure we have a stable branch.

Say you have to add a add the pull request 42 to OCA/sale-workflow.
You'll have to edit `odoo/pending-merges.yml` and add (or complete):

```yaml
./external-src/sale-workflow:
  remotes:
    oca: https://github.com/OCA/sale-workflow.git
    camptocamp: https://github.com/camptocamp/sale-workflow.git
  merges:
    - oca 9.0
    - oca refs/pull/42/head
  # you have to replace <project-id> here
  target: camptocamp merge-branch-<project-id>-master
```


Note: we always want the same `target` for all the repositories, so you can use YAML variables to write it only once, example:

```yaml
./external-src/bank-payment:
  ...
  target: &default_target camptocamp merge-branch-1151-master
./external-src/sale-workflow:
  ...
  target: *default_target
```

You can try to create the consolidated branch locally:

```bash
gitaggregator -c pending-merges.yml -d sale-workflow
```

And if you are happy with that, create a new Pull Request for the modification of the `pending-merges.yml` file.

## Merging a new pending merge

Once a new pull-request has been proposed with a change in `pending-merges.yml`,
we want to merge it as soon as possible in `master`, as it can be (and surely
is) a prerequisite for local developments.

If you are working on another branch than `master`, you'll want to use a
different name for the consolidation branch (the name of the consolidation
branch is the attribute `target` in `pending-merges.yml`).

This type of change is not done with a pull request:

1. on your local repository, merge the pull request having the
   `pending-merge.yml` change ([hub](https://hub.github.com) is a great plus for that)
2. rebuild and push the consolidation branch for the modified branch:

  ```
  gitaggregator -c pending-merges.yml -d sale-workflow -p
  ```

3. commit the git submodule change and push it on the `master` branch
