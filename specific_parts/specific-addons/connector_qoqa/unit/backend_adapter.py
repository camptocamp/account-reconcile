# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
import logging
import requests
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from openerp.addons.connector.exception import (NetworkRetryableError,
                                                RetryableJobError)

_logger = logging.getLogger(__name__)


class QoQaClient(object):

    def __init__(self, url, key, oauth_token):
        if not url.endswith('/'):
            url += '/'
        self.url = url
        self.key = key
        self.oauth_token = oauth_token

    def __getattr__(self, attr):
        return getattr(requests, attr)
    # TODO: add auth in post, get, put, delete, head, patch


class QoQaAdapter(CRUDAdapter):
    """ External Records Adapter for Trello """

    _endpoint = None  # to define in subclasses

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        assert self._endpoint, "_endpoint needs to be defined"
        super(QoQaAdapter, self).__init__(environment)
        # XXX: cache the connection informations?
        url = self.backend_record.url
        key = self.backend_record.key
        oauth = self.backend_record.oauth_token
        self.client = QoQaClient(url, key, oauth)
        self.version = self.backend_record.version
        self.lang = self.session.context['lang'][:2]

    @property
    def url(self):
        values = {'url': self.client.url,
                  'version': self.version,
                  'lang': self.lang,
                  'endpoint': self._endpoint,
                  }
        return "{url}api/{version}/{lang}/{endpoint}/".format(**values)

    def create(self, vals):
        # TODO: check
        record = self.client.post(self.url, params=vals)
        result = json.loads(record)
        return result['data']

    def read(self, id):
        record = self.client.get("{0}{1}".format(self.url, id))
        assert record['data']
        return record['data'][0]

    def search(self, id, only_ids=True):
        records = self.client.get(self.url)
        records = json.loads(records)
        if only_ids:
            return [r['id'] for r in records['data']]
        return records['data']
