#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Please propose your modification on
# https://github.com/camptocamp/odoo-template instead.
# Download submodules from Github zip archive url
# Keep standard update form private repositories
# listed in `travis/private_repo`
#
import os
import shutil
import urllib2
import yaml
import zipfile

from git import Repo

https_proxy = os.environ.get('https_proxy')
if https_proxy:
    proxy = urllib2.ProxyHandler({'https': https_proxy})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)

DL_DIR = 'download'
ZIP_PATH = '%s/submodule.zip' % DL_DIR

if os.path.exists(DL_DIR):  # clean if previous build failed
    shutil.rmtree(DL_DIR)
os.makedirs(DL_DIR)

with open('travis/private_repos') as f:
    private_repos = f.read()

os.system('git submodule init')

submodules = Repo('.').submodules


def git_url(url):
    """ Change an url to https and ending without .git all in lower case
    This to reuse it for archive download and to make it comparable.
    """
    url = url.lower()
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', 'https://github.com/')
    # remove .git
    if url.endswith('.git'):
        url = url[:-4]
    return url


# Check consitancy between .gitmodules and pending-merges.yaml
with open('odoo/pending-merges.yaml') as pending_yml:
    pending_merges = yaml.safe_load(pending_yml) or []

for sub in submodules:
    # replace odoo/ by ./
    pending_path = "." + sub.path[4:]
    if pending_path in pending_merges:
        pending = pending_merges[pending_path]
        target = pending['target'].split()[0]
        target_remote = pending['remotes'][target]
        assert git_url(target_remote) == git_url(sub.url.lower()), (
            "In .gitmodules %s :\n"
            "    remote url %s does not match \n"
            "    target url %s \n"
            "in pending-merges.yaml\n"
            "\n"
            "If you added pending merges entries you probably forgot to edit"
            " target in .gitmodules file to match the fork repository\n"
            "or if your intent is to clean up entries in pending-merges.yaml"
            " something went wrong in that file"
        ) % (sub.path, target_remote, sub.url)


for sub in submodules:
    print "Getting submodule %s" % sub.path
    use_archive = sub.path not in private_repos
    if use_archive:
        url = git_url(sub.url)
        archive_url = "%s/archive/%s.zip" % (url, sub.hexsha)
        request = urllib2.Request(archive_url)
        with open(ZIP_PATH, 'wb') as f:
            f.write(urllib2.urlopen(request).read())
        try:
            with zipfile.ZipFile(ZIP_PATH) as zf:
                zf.extractall(DL_DIR)
        except zipfile.BadZipfile:
            # fall back to standard download
            use_archive = False
            with open(ZIP_PATH) as f:
                print ("Getting archive failed with error %s. Falling back to "
                       "git clone." % f.read())
            os.remove(ZIP_PATH)
        except Exception as e:
            use_archive = False
            print ("Getting archive failed with error %s. Falling back to "
                   "git clone." % e.message)
        else:
            os.remove(ZIP_PATH)
            os.removedirs(sub.path)
            submodule_dir = os.listdir(DL_DIR)[0]
            shutil.move(os.path.join(DL_DIR, submodule_dir), sub.path)
    if not use_archive:
        os.system('git submodule update %s' % sub.path)
