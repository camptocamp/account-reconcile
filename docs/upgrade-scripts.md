# Upgrade scripts

## Stack

The upgrade system uses the following tools:

* [Marabunta](https://github.com/camptocamp/marabunta)
* [Anthem](https://github.com/camptocamp/anthem)

Marabunta is an orchestrator for running the migrations. Anthem runs Python
scripts provided with an Odoo environment. More details below.

Those tools are integrated in the image and can be configured using environment
variables. See the [Docker Odoo Project
readme](https://github.com/camptocamp/docker-odoo-project/#environment-variables)
for details on the variables.

## Marabunta

Marabunta expects a file named `migration.yml` in the `odoo` directory.
This `yaml` file contains the upgrade instructions for every version.
It creates a `marabunta_version` table in the database, containing the
installed versions, and run the upgrade scripts when a version is missing.

The upgrade instructions are composed of:
 * A list of commands executed before the installation/upgrade of the addons
 * The installation/upgrade of a list of addons
 * A list of commands executed after the installation/upgrade of the addons

Further, we can configure *modes* which allow to run additional commands when a
mode is activated (e.g. the 'demo' mode would load some demo data).

See [an example of yaml
file](https://github.com/camptocamp/marabunta/blob/master/marabunta/parser.py#L14-L61)

## Anthem

Anthem is a replacement for `oerpscenario`, but the scripts are written with
straight Python.

Simple example:

```python

import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def setup_company(ctx):
    """ Configuring company """
    company = ctx.env.ref('base.main_company')
    company.name = 'Rainbow Holding'


@anthem.log
def create_partners(ctx):
    """ Creating partners """
    names = [('Khiank Mountaingut', '__scenario.partner_1'),
             ('Kher Fernthorn', '__scenario.partner_2'),
             ('Sheing Coaldigger' '__scenario.partner_3'),
             ]
    for name, xmlid in names:
        create_or_update('res.partner', xmlid, {'name': name})


def main(ctx):
    setup_company(ctx)
    create_partners(ctx)

```

As you can see, each function takes a `ctx` argument. The `ctx` contains an
Odoo environment (`env`) which can be used exactly as we would do in Odoo.

Also, Anthem includes predefined functions for the common tasks (load csv
files, upsert a record with a xmlid, ...), called `lyrics`.

## Use cases

### Calling a song in migration.yml

Anthem takes the function we want to run as argument.
The syntax of the argument is `module-path::function-name`, where *module-path*
is the Python path of the module. So let's say we have a `main` function in
`songs/install/post.py`, the argument would be: `songs.install.post::main`.

In the `migration.yml` file, it means we have to add a pre/post operation in
the current version:

```yaml
    - version: 9.0.0
      operations:
        post:
          - anthem songs.install.post::main
```

### Run a single Anthem's song

As demonstrated in the previous section, anthem takes the function we want to
run as argument. So we can run a container the command line to execute the
desired function:

```
$ docker-compose run --rm odoo anthem songs.install.data_demo::create_partners
```

### Run a version upgrade again

By default, Marabunta won't execute a migration upgrade twice.
You can force it to execute an upgrade again with the `MARABUNTA_FORCE_VERSION`
environment variable:

```
$ docker-compose run --rm -e MARABUNTA_FORCE_VERSION=9.0.0 odoo
```

With the command above, odoo will be run at the end of the migration.
You could also run only `migrate` which will exit the container once done.

```
$ docker-compose run --rm -e MARABUNTA_FORCE_VERSION=9.0.0 odoo migrate
```

### Execute the upgrade for a given mode

Modes allow to run additional commands.

```yaml
  versions:
    - version: 9.0.0
      operations:
        pre:
          - anthem songs.install.pre::main
        post:
          - anthem songs.install.post::main
      addons:
        upgrade:
          - account
      modes:
        full:
          operations:
            pre:
              - anthem songs.install.pre_full::main
            post:
              - anthem songs.install.data_full::main
        demo:
          operations:
            post:
              - anthem songs.install.data_demo::main
          addons:
            upgrade:
              - demo_addon
```

In the example above, we have 2 modes: `full` and `demo`. We use them to spawn
different types of instances, `demo` might be used for a development instance
or a test server, the full one for the production (possibly with a lot of
data).

Mode's commands are always executed after the main ones, the addons lists are merged.
The order of execution when no mode is used will be:

1. `anthem songs.install.pre::main`
2. `-i account` (or `-u` if it is already installed)
3. `anthem songs.install.post::main`

When the demo mode is used (`MARABUNTA_MODE=demo`):

1. `anthem songs.install.pre::main`
2. `-i account,demo_addon` (or `-u` if it is already installed)
3. `anthem songs.install.post::main`
4. `anthem songs.install.data_demo::main`

When the full mode is used (`MARABUNTA_MODE=full`):

1. `anthem songs.install.pre::main`
1. `anthem songs.install.pre_full::main`
2. `-i account` (or `-u` if it is already installed)
3. `anthem songs.install.post::main`
4. `anthem songs.install.data_full::main`

Usually, the `MARABUNTA_MODE` will be set in the `docker-compose.yml`
composition files, but you can also set in when running a container:

```
$ docker-compose run --rm -e MARABUNTA_MODE=demo odoo
```

### Disable the migration

When you don't want the migration to run at all, you can disable it with:

```
$ docker-compose run --rm -e MIGRATE=False odoo
```
