<!--
This file has been generated with 'invoke project.sync'.
Do not modify. Any manual change will be lost.
Please propose your modification on
https://github.com/camptocamp/odoo-template instead.
-->
# Using automated tasks with Invoke

This project uses `invoke` to run some automated tasks.

First, install it with:

```bash

$ pip install -r tasks/requirements.txt

```

You can now see the list of tasks by running at the root directory:

```bash

$ invoke --list

```

The tasks are defined in `tasks.py`.

## Some tasks

### release.bump

release.bump is used to bump the current version number:
(see [releases.md](docs/releases.md#versioning-pattern) for more informations about versionning)

```
invoke release.bump --feature
# or
invoke release.bump --patch
```

--feature will change the minor version number (eg. 9.1.0 to 9.2.0).
--patch will change the patch version number (eg 9.1.0 to 9.1.1).

bump.release changes following files (which must be commited):
 * [odoo/VERSION](../odoo/VERSION): just contains the project version number, so this version is changed.
 * [HISTORY.rst](../HISTORY.rst): Rename Unreleased section with the new version number and create a new unreleased section.
 * rancher/integration/docker-compose.yml: Change the version of the docker image to use for the integration stack.

### project.sync

Copy files (such as docs) from the
[odoo-template](https://github.com/camptocamp/odoo-template).
It should be run at a regular basis.

```
invoke project.sync
```

### translate.generate

It generates or updates the pot translation file for an addon.
A new database will be created by the task, in which the addon will be
installed, so we guaranteed to have clean terms.

```
invoke translate.generate odoo/local-src/my_addon
# or
invoke translate.generate odoo/external-src/sale-workflow/my_addon

```

### submodule.init

Add git submodules from the `.gitmodules` file configuration.
Instead of using `git submodule add -b 9.0 {url}`
{path}, for every branch you need to add, you can edit the `.gitmodules` file,
add the entries you want, and run this command.


```
invoke submodule.init
```

### submodule.list

List submodules paths which can be directly used to directly copy-paste the
addons paths in the Dockerfile. The order depends of the order in the
.gitmodules file.

```
invoke submodule.list
```

### submodule.merges

Generate and push a branch including the pending pull requests.

```
invoke submodule.merges odoo/external-src/sale-workflow
```


### submodule.show-closed-prs

Show a list of closed pull requests in the pending merges.

```
invoke submodule.show-closed-prs
```

### songs.rip

Copy generated songs of a dj.compilation
They come as a zip file which can loaded from a local path or from an odoo url
Files will be placed according to their path in zip file with ./odoo as the root.

When providing an url you can set authentication parameters for the odoo from which
you want to download the compilation.

Usually songs and csv data will be copied in:

odoo/songs/install/generated
and
odoo/data/install/generated

See https://github.com/camptocamp/odoo-dj for more details about dj.compilation


```
invoke songs.rip http://127.0.0.1:8888/dj/download/compilation/account-default-1 [--login admin] [--password admin] [--db odoodb]
# or
invoke songs.rip /tmp/songs.zip
```

## Custom tasks

Alongside the core namespaces (release, project. translate), you can create
your own namespace for the need of the project. Dropping a Python file with an
invoke `@task` in the `tasks` directory will make it available in the `invoke`
commands. The namespace will be the name of the file. Let's say you add a
function named `world` decorated with `@task` in a file named `hello.py`, then
the command will be `invoke hello.world`.
