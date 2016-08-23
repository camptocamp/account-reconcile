# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

import fileinput
import os
import re

from contextlib import contextmanager
from datetime import date
from distutils.version import StrictVersion

import yaml

from invoke import task, exceptions, Collection


ns = Collection()
release = Collection('release')
ns.add_collection(release)


def build_path(path, from_file=None):
    if from_file is None:
        from_file = __file__
    return os.path.join(os.path.dirname(os.path.realpath(from_file)), path)


PROJECT_ID = '1151'
VERSION_FILE = build_path('odoo/VERSION')
VERSION_RANCHER_FILES = (
    build_path('rancher/integration/docker-compose.yml'),
)
HISTORY_FILE = build_path('HISTORY.rst')
DOCKER_IMAGE = 'camptocamp/qoqa_openerp'
PENDING_MERGES = build_path('odoo/pending-merges.yaml')
GIT_REMOTE_NAME = 'camptocamp'


def exit_msg(message):
    print(message)
    raise exceptions.Exit(1)


@contextmanager
def cd(path):
    prev = os.getcwd()
    os.chdir(os.path.expanduser(path))
    try:
        yield
    finally:
        os.chdir(prev)


def _current_version():
    with open(VERSION_FILE, 'rU') as fd:
        version = fd.read().strip()
    return version


def _check_git_diff(ctx):
    try:
        ctx.run('git diff --quiet --exit-code')
        ctx.run('git diff --cached --quiet --exit-code')
    except exceptions.Failure:
        r = raw_input('Your repository has local changes, '
                      'are you sure you want to continue? (y/N) ')
        if r not in ('y', 'Y', 'yes'):
            exit_msg('Aborted')


@task
def bump(ctx, feature=False, patch=False):
    """ Increase the version number where needed """
    if not (feature or patch):
        exit_msg("should be a --feature or a --patch version")
    old_version = _current_version()
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
        fd.write(version + '\n')

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
            print("\n**Data Migration**\n\n"
                  "**Features and Improvements**\n\n"
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


@task
def push_branches(ctx):
    """ Push the local branches to the camptocamp remote

    The branch name will be composed of the id of the project and the current
    version number (the one in odoo/VERSION).

    It should be done at the closing of every release, so we are able
    to build a new patch branch from the same commits if required.
    """
    version = _current_version()
    branch_name = 'merge-branch-{}-{}'.format(PROJECT_ID, version)
    response = raw_input(
        'push local branches to {}? (y/N) '.format(branch_name)
    )
    _check_git_diff(ctx)
    if response not in ('y', 'Y', 'yes'):
        exit_msg('Aborted')
    with open(PENDING_MERGES, 'ru') as f:
        merges = yaml.load(f.read())
        for path in merges:
            with cd(build_path(path, from_file=PENDING_MERGES)):
                ctx.run(
                    'git push -f -v {} HEAD:refs/heads/{}'
                    .format(GIT_REMOTE_NAME, branch_name)
                )


release.add_task(bump, 'bump')
release.add_task(push_branches, 'push-branches')
