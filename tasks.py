# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

import fileinput
import glob
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
translate = Collection('translate')
ns.add_collection(translate)


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
MIGRATION_FILE = build_path('odoo/migration.yml')


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
    if response not in ('y', 'Y', 'yes'):
        exit_msg('Aborted')
    _check_git_diff(ctx)
    with open(PENDING_MERGES, 'ru') as f:
        merges = yaml.load(f.read())
        for path, setup in merges.iteritems():
            print('pushing {}'.format(path))
            with cd(build_path(path, from_file=PENDING_MERGES)):
                try:
                    ctx.run(
                        'git config remote.{}.url'.format(GIT_REMOTE_NAME)
                    )
                except exceptions.Failure:
                    remote_url = setup['remotes'][GIT_REMOTE_NAME]
                    ctx.run(
                        'git remote add {} {}'.format(GIT_REMOTE_NAME,
                                                      remote_url)
                    )
                ctx.run(
                    'git push -f -v {} HEAD:refs/heads/{}'
                    .format(GIT_REMOTE_NAME, branch_name)
                )


@task(post=[push_branches])
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

    try:
        ctx.run(r'grep --quiet --regexp "- version:.*{}" {}'.format(
            version,
            MIGRATION_FILE
        ))
    except exceptions.Failure:
        with open(MIGRATION_FILE, 'a') as fd:
            fd.write('    - version: {}\n'.format(version))

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


release.add_task(bump, 'bump')
release.add_task(push_branches, 'push-branches')


@task(default=True)
def translate_generate(ctx, addon_path, update_po=True):
    """ Generate pot template and merge it in language files

    Example:

        $ invoke translate.generate odoo/local-src/my_module
    """
    dbname = 'tmp_generate_pot'
    addon = addon_path.split('/')[-1]
    assert os.path.exists(build_path(addon_path)), "%s not found" % addon_path
    container_path = os.path.join('/opt', addon_path, 'i18n')
    i18n_dir = os.path.join(build_path(addon_path), 'i18n')
    if not os.path.exists(i18n_dir):
        os.mkdir(i18n_dir)
    container_po_path = os.path.join(container_path, '%s.po' % addon)
    user_id = ctx.run(['id --user'], hide='both').stdout.strip()
    cmd = ('docker-compose run --rm  -e LOCAL_USER_ID=%(user)s '
           '-e DEMO=False -e MIGRATE=False odoo odoo.py '
           '--log-level=warn --workers=0 '
           '--database %(dbname)s --i18n-export=%(path)s '
           '--modules=%(addon)s --stop-after-init --without-demo=all '
           '--init=%(addon)s') % {'user': user_id, 'path': container_po_path,
                                  'dbname': dbname, 'addon': addon}
    ctx.run(cmd)

    ctx.run('docker-compose run --rm -e PGPASSWORD=odoo odoo '
            'dropdb %s -U odoo -h db' % dbname)

    # mv .po to .pot
    source = os.path.join(i18n_dir, '%s.po' % addon)
    pot_file = source + 't'
    ctx.run('mv %s %s' % (source, pot_file))

    if update_po:
        for po_file in glob.glob('%s/*.po' % i18n_dir):
            ctx.run('msgmerge %(po)s %(pot)s -o %(po)s' %
                    {'po': po_file, 'pot': pot_file})
    print('%s.pot generated' % addon)

translate.add_task(translate_generate, 'generate')
