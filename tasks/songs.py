# -*- coding: utf-8 -*-
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Please propose your modification on
# https://github.com/camptocamp/odoo-template instead.
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from __future__ import print_function

from StringIO import StringIO
import urllib2
import zipfile
from urlparse import urlparse
try:
    from requests import Request, Session
except ImportError:
    print('Please install requests')
import json

from invoke import task

from .common import exit_msg


def odoo_login(base_url, login, password, db):
    """ Get a session_id from Odoo """
    url = "%s/web/session/authenticate" % base_url

    s = Session()

    data = {
        'jsonrpc': '2.0',
        'params': {
            'context': {},
            'db': db,
            'login': login,
            'password': password,
        },
    }

    headers = {
        'Content-type': 'application/json'
    }

    req = Request('POST', url, data=json.dumps(data), headers=headers)
    prepped = req.prepare()
    resp = s.send(prepped)

    r_data = json.loads(resp.text)
    return r_data['result']['session_id']


@task(name='rip')
def rip(ctx, location, login='admin', password='admin',
        db='odoodb'):
    """ Open or download a zipfile containing songs

    Unzip and copy the files into current project path

    location: url or file path

    url is meant for an odoo url you can set login, password and db

    """
    if not location:
        exit_msg(
            "You must provide a value for --location\n"
            "It can be an url or a local path\n\n"
            "invoke songs.rip /tmp/songs.zip\n"
            "invoke songs.rip "
            "http://project:8888/dj/download/compilation/account-default-1")
    zipdata = None
    # download file from url
    if location.startswith('http'):
        url = urlparse(location)
        base_url = "%s://%s" % (url.scheme, url.netloc)
        session_id = odoo_login(base_url, login, password, db)
        req = urllib2.Request(location)
        req.add_header('cookie', "session_id=%s" % session_id)
        response = urllib2.urlopen(req)
        zipdata = StringIO()
        zipdata.write(response.read())
    else:
        zipdata = open(location)
    zf = zipfile.ZipFile(zipdata)

    # Unzip file and push files at the right path
    readme_path = None
    for path in zf.namelist():
        # Ignore dj metadata zip file
        if path.endswith('zip'):
            continue
        if 'DEV_README.rst' in path:
            readme_path = path
        else:
            print("Extracting ./odoo/%s" % path)
            zf.extract(path, './odoo')

    print('-' * 79)
    # Print README file
    print(zf.open(readme_path).read())
