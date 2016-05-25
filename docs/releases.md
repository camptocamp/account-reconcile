# Releases

## Release process

In the following order, at the end of a sprint, the release master will do:

* merge all pending pull requests when possible
* Generate the new 'pending-merge' branches with a name corresponding to the tag (`pending-merge-<project-id>-<version>`):

  ```bash
  cd odoo
  vi pending-merges.yml  # change target name
  gitaggregate -c pending-merges.yml -p
  git checkout -- pending-merges.yml
  # revert the target name in odoo/pending-merges.yml, we don't want to write
  # to those stable branches again
  ```

* do the verifications: migration scripts, changelog
* once all seems well, the release master adds a tag according to
  the [versioning pattern] (#Versioning pattern) using:

  ```
  git tag -a x.y.z
  git push --tags
  ```
When the tag is pushed on GitHub, Travis will build a new Docker image (as
long as the build is green!) and push it on the registry as `camptocamp/qoqa_openerp:x.y.z`

## Versioning pattern

The version is in the form `x.y.z` where:

* **x** is the major number, always equal to the Odoo version (9.x.z)
* **y** is the minor number, incremented at the end of each sprint, this is
  were new features are added
* **z** is the patch number, incremented for corrections on production releases.

All the developments are done on the `master` branch and a new release on
`master` implies a new `minor` version increment.
When there is an issue with a released image after the tag has been set, a
patch branch is created from the tag and a new release is done from this
branch; the patch number is incremented.

Example of branches involving Paul as the Release Master and Liza and Greg as
developers, the current version is `9.3.2`:

* Liza works on a new feature so she creates a branch for master:

```
git branch origin/master -b impl-stock-split
git push liza/impl-stock-split
```

* Greg works on a new feature too:
```
git branch origin/master -b impl-crm-claim-email
git push greg/impl-crm-claim-email
```
* The end of sprint is close, both propose their branches as pull requests in
  `master`, builds are green!
* Paul merges the pull requests, prepares a new release and when he's done, he
  tags `master` with `9.4.0`
* Paul tests the image `camptocamp/qoqa_openerp:9.4.0` and oops, it seems he
  goofed as the image doesn't even start
* Paul corrects the - hopefully - minor issue and prepare a new release for
  `9.4.1`.
* Liza works on another shiny feature:
```
git branch origin/master -b impl-blue-css
git push liza/impl-blue-css
```
* And Greg is assigned to fix a bug on the production server (now in `9.4.1`),
  so he will do 2 things:
  * create a patch branch *from* the production version:
  ```
  git branch origin/9.4.1 -b patch-claim-typo
  git push greg/patch-claim-typo
  ```
  * ask Paul to create a new patch branch `patch-9.4.2`, on which he will
    propose his pull request
* Paul prepare a new release on the `patch-9.4.2` branch. Once released, Paul merges `patch-9.4.2` in `master`.
* At the end of the sprint, Paul prepares the next release `9.5.0` with the new Liza's feature and so on.

## Release master

At the end of a sprint, the release master will create a new release.
There is one release master at a time, but the person assuming this role may
change over the life of the project.

The release master checks the following points before doing a release:

* migration scripts are complete and working
* there are no conflicts between the merged branches (but he might ask to the
  other developers to resolve them)
* complete and correct the [changelog](../HISTORY.rst).
* check and update the docker-compose files if necessary
* ensure Travis is green

Then, he checks that the released Docker image works well.

Overall, his role is to ensure that all is well and smooth for a release.
