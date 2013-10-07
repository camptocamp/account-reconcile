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
from requests_oauthlib import OAuth1
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from openerp.addons.connector.exception import (NetworkRetryableError,
                                                RetryableJobError)
from ..exception import QoQaResponseNotParsable

_logger = logging.getLogger(__name__)


class QoQaClient(object):

    def __init__(self, base_url, client_key, client_secret,
                 access_token, access_token_secret, debug=False):
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.debug = debug
        self._client_key = client_key
        self._client_secret = client_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._session = None
        self._auth = OAuth1(
            self._client_key,
            client_secret=self._client_secret,
            resource_owner_key=self._access_token,
            resource_owner_secret=self._access_token_secret)

    def __getattr__(self, attr):
        """ Forward attributes to ``requests``.

        This allows to call a ``post`` or ``get`` directly
        on a ``QoQaClient`` instance.

        It automatically adds the ``auth`` keyword argument
        to the request with the OAuth1 tokens.

        When the debug mode is activated, it disables the check
        on the SSL certificat.
        """
        dispatch = getattr(requests, attr)
        def with_auth(*args, **kwargs):
            kwargs['auth'] = self._auth
            return dispatch(*args, **kwargs)
        if self.debug:
            def with_debug(*args, **kwargs):
                kwargs['verify'] = False
                return with_auth(*args, **kwargs)
            return with_debug
        return with_auth


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
        # XXX: cache the connection informations
        backend = self.backend_record
        args = (backend.url,
                backend.client_key or '',
                backend.client_secret or '',
                backend.access_token or '',
                backend.access_token_secret or '')
        self.client = QoQaClient(*args, debug=backend.debug)
        self.version = self.backend_record.version
        self.lang = self.session.context['lang'][:2]

    def url(self):
        values = {'url': self.client.base_url,
                  'version': self.version,
                  'lang': self.lang,
                  'endpoint': self._endpoint,
                  }
        return "{url}api/{version}/{lang}/{endpoint}/".format(**values)

    def _handle_response(self, response):
        _logger.debug("%s %s returned %s %s", response.request.method,
                      response.url, response.status_code, response.reason)
        if response.request.method == 'POST':
            _logger.debug("The POST body was: %s", response.request.body)
        response.raise_for_status()
        try:
            parsed = json.loads(response.content)
        except ValueError as err:
            raise QoQaResponseNotParsable(err)
        return parsed

    def create(self, vals):
        url = self.url()
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.post(url, data=json.dumps(vals),
                                    headers=headers)
        result = self._handle_response(response)
        return result['data']

    def read(self, id):
        url = "{0}{1}".format(self.url(), id)
        response = self.client.get(url)
        result = self._handle_response(response)
        assert result['data']
        return result['data'][0]

    def search(self, id, only_ids=True):
        url = self.url()
        response = self.client.get(url)
        records = self._handle_response(response)
        if only_ids:
            return [r['id'] for r in records['data']]
        return records['data']
