[![Build Status](https://travis-ci.com/camptocamp/qoqa_openerp.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://travis-ci.com/camptocamp/qoqa_openerp)

# QoQa Odoo

**Our internal id for this project is: 1151.**

This project uses Docker.
Travis builds a new image for each change on the branches and for each new tag.

The images built on the master branch are built as `camptocamp/qoqa_openerp:latest`.
The images built on other branches are built as `camptocamp/qoqa_openerp:<branch-name>`.
The ones built from tags are built as `camptocamp/qoqa_openerp:<tag-name>`.

Images are pushed on the registry only when Travis has a green build.

When a container starts, the database is automatically created and the
migration scripts automatically run.

## Project maintenance

Please keep this project up-to-date by:

* ensure the `FROM` image in `odoo/Dockerfile` is the latest release
* run regularly `invoke project.sync` to retrieve the last template's changes

## Links

* [General documentation](./docs/README.md)
* [Local documentation](./docs/README.local.md)
* [Changelog](HISTORY.rst).
* [Minions](https://qoqa_openerp.odoo-test.camptocamp.ch)
* [Base image documentation](https://github.com/camptocamp/docker-odoo-project)
