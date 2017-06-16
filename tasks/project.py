# -*- coding: utf-8 -*-
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from __future__ import print_function

import fnmatch
import os
import shutil

import yaml

from invoke import task

from .common import (
    exit_msg,
    check_git_diff,
    tempdir,
    cookiecutter_context,
    TEMPLATE_GIT,
    cd,
    root_path,
)

try:
    from cookiecutter.main import cookiecutter
except ImportError:
    cookiecutter = None


def _exclude_fnmatch(root, files, exclude):
    return list(set(files) -
                set([d for d in files for excl in exclude
                     if fnmatch.fnmatch(os.path.join(root, d), excl)]))


def _add_comment_unknown(path, comment):
    print('No function to add a comment in {}'.format(path))


def _add_comment_py(path, comment):
    with open(path, 'rU') as f:
        content = f.readlines()
    insert_at = 0
    for index, line in enumerate(content):
        if line.startswith('#!'):
            insert_at = index + 1
        if 'coding:' in line:
            insert_at = index + 1
            break
    comment = '\n'.join(['# {}'.format(line) for line in comment.splitlines()])
    comment += '\n'
    content.insert(insert_at, comment)
    with open(path, 'w') as f:
        f.write(''.join(content))


def _add_comment_md(path, comment):
    with open(path, 'rU') as f:
        content = f.readlines()
    insert_at = 0
    comment = '<!--\n{}-->\n'.format(comment)
    content.insert(insert_at, comment)
    with open(path, 'w') as f:
        f.write(''.join(content))


def _add_comment_sh(path, comment):
    with open(path, 'rU') as f:
        content = f.readlines()
    insert_at = 0
    for index, line in enumerate(content):
        if line.startswith('#!'):
            insert_at = index + 1
    comment = '\n'.join(['# {}'.format(line) for line in comment.splitlines()])
    comment += '\n'
    content.insert(insert_at, comment)
    with open(path, 'w') as f:
        f.write(''.join(content))


def add_comment(path, comment):
    __, ext = os.path.splitext(path)
    funcs = {
        '.py': _add_comment_py,
        '.md': _add_comment_md,
        '.sh': _add_comment_sh,
    }
    if not ext:
        with open(path, 'rU') as f:
            line = f.readline()
            if line.startswith('#!'):
                if 'python' in line:
                    ext = '.py'
                if 'sh' in line:
                    ext = '.sh'

    funcs.get(ext, _add_comment_unknown)(path, comment)


@task
def sync(ctx, commit=True):
    """ Sync files from the project template """
    if not cookiecutter:
        exit_msg('cookiecutter must be installed')
    check_git_diff(ctx, direct_abort=True)
    context = cookiecutter_context()
    os.chdir(root_path())
    with tempdir() as tmp:
        cookiecutter(
            TEMPLATE_GIT,
            no_input=True,
            extra_context=context,
            output_dir=tmp,
            overwrite_if_exists=True,
        )
        template = os.path.join(tmp, context['repo_name'])
        selected_files = set()
        with cd(template):
            with open(os.path.join(template, '.sync.yml'), 'rU') as syncfile:
                sync = yaml.load(syncfile.read())
                include = sync['sync'].get('include', [])
                exclude = sync['sync'].get('exclude', [])
                comment = sync['sync'].get('comment', '')
                for root, dirs, files in os.walk('.', topdown=True):
                    if exclude:
                        dirs[:] = _exclude_fnmatch(root, dirs, exclude)
                        files[:] = _exclude_fnmatch(root, files, exclude)
                    syncfiles = [os.path.join(root, f) for f in files]
                    for incl in include:
                        selected_files.update(fnmatch.filter(syncfiles, incl))

            print('Syncing files:')
            for s in sorted(selected_files):
                print('* {}'.format(s))

        for relpath in selected_files:
            source = os.path.join(template, relpath)
            target_dir = os.path.dirname(relpath)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.copy(source, relpath)
            if os.path.isfile(relpath):
                add_comment(relpath, comment)

        ctx.run('git add {}'.format(' '.join(selected_files)))
        if commit:
            ctx.run('git commit -m "Update project from odoo-template" -e -vv',
                    pty=True)
