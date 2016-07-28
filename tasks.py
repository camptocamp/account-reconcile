# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

import fileinput
import re

from datetime import date
from distutils.version import StrictVersion

from invoke import task, exceptions


VERSION_FILE = 'odoo/VERSION'
VERSION_RANCHER_FILES = ('rancher/integration/docker-compose.yml',)
HISTORY_FILE = 'HISTORY.rst'
DOCKER_IMAGE = 'camptocamp/qoqa_openerp'


def exit_msg(message):
    print(message)
    raise exceptions.Exit(1)


@task
def bump(ctx, feature=False, patch=False):
    if not (feature or patch):
        exit_msg("should be a --feature or a --patch version")
    with open(VERSION_FILE, 'rU') as fd:
        old_version = fd.read().strip()
    if not old_version:
        exit_msg("the version file is empty")
    try:
        version = StrictVersion(old_version)
    except ValueError:
        exit_msg("'{}' is not a valid version".format(version))

    if not len(version.version) == 3:
        exit_msg("'{}' should be x.y.z".format(version.version))

    if feature:
        version = (version.version[0],
                   version.version[1] + 1,
                   0)
    elif patch:
        version = (version.version[0],
                   version.version[1],
                   version.version[2] + 1)
    version = '.'.join([str(v) for v in version])
    with open(VERSION_FILE, 'w') as fd:
        fd.write(version)

    pattern = r'^(\s*)image:\s+{}:\d+.\d+.\d+$'.format(DOCKER_IMAGE)
    replacement = r'\1image: {}:{}'.format(DOCKER_IMAGE, version)
    for rancher_file in VERSION_RANCHER_FILES:
        # with fileinput, stdout is redirected to the file in place
        for line in fileinput.input(rancher_file, inplace=True):
            if DOCKER_IMAGE in line:
                print(re.sub(pattern, replacement, line), end='')
            else:
                print(line, end='')

    new_version_index = None
    for index, line in enumerate(fileinput.input(HISTORY_FILE, inplace=True)):
        # Weak heuristic to find where we should write the new version
        # header, anyway, it will need manual editing to have a proper
        # changelog
        if 'unreleased' in line.lower():
            # place the new header 2 lines after because we have the
            # underlining
            new_version_index = index + 2
        if index == new_version_index:
            today = date.today().strftime('%Y-%m-%d')
            new_version_header = "{} ({})".format(version, today)
            print("\n**Features and Improvements**\n\n"
                  "**Bugfixes**\n\n"
                  "**Build**\n\n"
                  "**Documentation**\n\n\n"
                  "{}\n"
                  "{}".format(new_version_header,
                              '+' * len(new_version_header)))

        print(line, end='')

    print('version changed to {}'.format(version))
    print('you should probably clean {}'
          '(remove empty sections, whitespaces, ...)'.format(HISTORY_FILE))
    print('and commit + tag the changes')
