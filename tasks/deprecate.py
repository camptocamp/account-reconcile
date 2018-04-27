# -*- coding: utf-8 -*-
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Please propose your modification on
# https://github.com/camptocamp/odoo-template instead.
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from __future__ import print_function

import os

try:
    from ruamel.yaml import YAML
except ImportError:
    print('Please install ruamel.yaml')

from invoke import task
from .common import (
    MIGRATION_FILE,
    build_path,
    search_replace,
)


@task(name='demo-to-sample')
def demo_to_sample(ctx):
    """ Renaming of demo to sample for MARABUNTA_MODE

    This intend to fix files that aren't synced

    It will edit the following files:
    - .travis.yml
    - docker-compose.overide.yml
    - odoo/migration.yml
    - odoo/songs/install/data_all.py (for comment)
    - test.yml
    - travis/minion-files/rancher.list

    It will move:
    - odoo/data/demo to odoo/data/sample
    - odoo/songs/install/data_demo.py to odoo/songs/sample/data_sample.py

    """
    change_list = []
    # .travis.yml
    path = build_path('.travis.yml')
    search_replace(
        path,
        '-e MARABUNTA_MODE=demo',
        '-e MARABUNTA_MODE=sample')
    change_list.append(path)

    # docker-compose.overide.yml
    path = build_path('docker-compose.override.yml')
    search_replace(
        path,
        '- MARABUNTA_MODE=demo',
        '- MARABUNTA_MODE=sample')
    change_list.append(path)

    # odoo/migration.yml
    path = MIGRATION_FILE
    search_replace(
        path,
        'anthem songs.install.data_demo',
        'anthem songs.sample.data_sample')
    change_list.append(path)

    yaml = YAML()
    # preservation of indentation
    yaml.indent(mapping=2, sequence=4, offset=2)

    # change demo: keys to sample:
    with open(MIGRATION_FILE) as f:
        data = yaml.load(f.read())

    data['migration']['versions']
    for x in data['migration']['versions']:
        if 'modes' in x and 'demo' in x['modes']:
            x['modes']['sample'] = x['modes']['demo']
            del x['modes']['demo']

    with open(MIGRATION_FILE, 'w') as f:
        yaml.dump(data, f)

    # test.yml
    path = build_path('odoo/songs/install/data_all.py')
    search_replace(
         path,
         "The data loaded here will be loaded in the 'demo' and",
         "The data loaded here will be loaded in the 'sample' and")
    change_list.append(path)

    # test.yml
    path = build_path('test.yml')
    search_replace(
        path,
        '- MARABUNTA_MODE=demo',
        '- MARABUNTA_MODE=sample')
    change_list.append(path)

    # travis/minion-files/rancher.list
    path = build_path('travis/minion-files/rancher.list')
    search_replace(
         path,
         'MARABUNTA_MODE=demo',
         'MARABUNTA_MODE=sample')
    change_list.append(path)

    ctx.run('git add {}'.format(' '.join(change_list)))

    folder = 'odoo/data/sample'
    try:
        os.mkdir(folder, 0o775)
    except OSError:
        print("odoo/data/sample directory already exists")
    # move odoo/data/demo to odoo/data/sample
    try:
        ctx.run(
            'git mv {} {}'.format(
                'odoo/data/demo/*',
                'odoo/data/sample'))
    except Exception:
        print('nothing to move')

    # move odoo/songs/install/data_demo.py to odoo/songs/sample/data_sample.py
    folder = 'odoo/songs/sample'
    try:
        os.mkdir(folder, 0o775)
        with open(folder + '/__init__.py', 'w') as f:
            f.write('')
    except OSError:
        print("odoo/songs/sample directory already exists")
    try:
        ctx.run(
            'git mv {} {}'.format(
                'odoo/songs/install/data_demo.py',
                'odoo/songs/sample/data_sample.py'))
    except Exception:
        print('nothing to move')

    # Change strings referencing 'data/demo' to 'data/sample'
    path = build_path('odoo/songs/sample/data_sample.py')
    search_replace(
         path,
         'data/demo',
         'data/sample')
    change_list.append(path)

    ctx.run('git add odoo/songs/sample')

    print("Deprecation applied")
    print()
    print("The following files were checked and modified:")
    print("- .travis.yml")
    print("- docker-compose.overide.yml")
    print("- odoo/migration.yml")
    print("- odoo/songs/install/data_all.py (for comment)")
    print("- odoo/songs/install/data_demo.py (path 'data/demo' to "
          "'data/sample')")
    print("- test.yml")
    print("- travis/minion-files/rancher.list")

    print()
    print("The following files were moved:")
    print("- odoo/data/demo to odoo/data/sample")
    print("- odoo/songs/install/data_demo.py to odoo/songs/sample/data_sample"
          ".py")
    print()
    print("Please check your staged files:")
    print("   git diff --cached")
    print("Please search for any unchanged 'demo' string in odoo/songs "
          "and fix it manually.")
    print("If everything is good:")
    print("   git commit -m 'Apply depreciation of demo in favor of sample'")
    print("      git push")
