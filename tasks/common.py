# -*- coding: utf-8 -*-
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import errno
import os
import shutil
import tempfile
import yaml

from contextlib import contextmanager
from invoke import exceptions


def root_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def build_path(path, from_root=True, from_file=None):
    assert not (from_root and from_file)
    if from_root:
        base_path = root_path()
    else:
        if from_file is None:
            from_file = __file__
        base_path = os.path.dirname(os.path.realpath(from_file))

    return os.path.join(base_path, path)


VERSION_FILE = build_path('odoo/VERSION')
HISTORY_FILE = build_path('HISTORY.rst')
PENDING_MERGES = build_path('odoo/pending-merges.yaml')
GIT_REMOTE_NAME = 'camptocamp'
MIGRATION_FILE = build_path('odoo/migration.yml')
TEMPLATE_GIT = 'git@github.com:camptocamp/odoo-template.git'
COOKIECUTTER_CONTEXT = build_path('.cookiecutter.context.yml')


def cookiecutter_context():
    with open(COOKIECUTTER_CONTEXT, 'rU') as f:
        return yaml.load(f.read())


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


def current_version():
    with open(VERSION_FILE, 'rU') as fd:
        version = fd.read().strip()
    return version


def check_git_diff(ctx, direct_abort=False):
    try:
        ctx.run('git diff --quiet --exit-code')
        ctx.run('git diff --cached --quiet --exit-code')
    except exceptions.Failure:
        if direct_abort:
            exit_msg('Your repository has local changes. Abort.')
        r = raw_input('Your repository has local changes, '
                      'are you sure you want to continue? (y/N) ')
        if r not in ('y', 'Y', 'yes'):
            exit_msg('Aborted')


@contextmanager
def tempdir():
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        try:
            shutil.rmtree(name)
        except OSError as e:
            # already deleted
            if e.errno != errno.ENOENT:
                raise
