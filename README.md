[![Build Status](https://magnum.travis-ci.com/camptocamp/qoqa_openerp.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://magnum.travis-ci.com/camptocamp/qoqa_openerp)

# QoQa OpenERP

Private and customer specific branches for QoQa.

## Installation:

Steps:

1. Create a file with name `buildout.cfg` containing:

    [buildout]
    extends = profiles/dev.cfg

2. Bootstrap & build

    ./bootstrap.sh
    bin/buildout


:warning: do not extend the other configuration files if you do not know what you
are doing

## Travis testing

This repository is tested against Travis.
The Pull Requests must conform to
[pep8](http://legacy.python.org/dev/peps/pep-0008/).
The lint command used is:

    flake8 specific-parts/specific-addons --exclude=__init__.py
