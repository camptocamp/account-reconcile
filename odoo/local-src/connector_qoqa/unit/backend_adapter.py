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
from requests.exceptions import HTTPError, RequestException, ConnectionError
from contextlib import contextmanager
from requests_oauthlib import OAuth1
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from openerp.addons.connector.exception import NetworkRetryableError
from ..exception import (QoQaResponseNotParsable,
                         QoQaAPISecurityError,
                         QoQaResponseError,
                         )

_logger = logging.getLogger(__name__)

REQUESTS_TIMEOUT = 30  # seconds

# Add detailed logs
# import httplib
# httplib.HTTPConnection.debuglevel = 1
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


@contextmanager
def api_handle_errors(message):
    """ Handle error when calling the API

    It is meant to be used when a model does a direct
    call to a job using the API (not using job.delay()).
    Avoid to have unhandled errors raising on front of the user,
    instead, they are presented as ``orm.except_orm``.
    """
    try:
        yield
    except NetworkRetryableError as err:
        raise orm.except_orm(_('Network Error'), (message + '\n\n%s') % err)
    except (HTTPError, RequestException, ConnectionError) as err:
        raise orm.except_orm(_('API / Network Error'),
                             (message + '\n\n%s') % err)
    except QoQaAPISecurityError as err:
        raise orm.except_orm(_('Authentication Error'),
                             (message + '\n\n%s') % err)
    except QoQaResponseError as err:
        raise orm.except_orm(_('Error(s) returned by QoQa'), unicode(err))
    except QoQaResponseNotParsable:
        # The response from the backend cannot be parsed, not a
        # JSON.  So we don't know what the error is.
        _logger.exception(message)
        raise orm.except_orm(_('Unknown Error'), message)


class QoQaClient(object):

    retryable = (requests.exceptions.Timeout,
                 requests.exceptions.ConnectionError,
                 )

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
            try:
                return dispatch(timeout=REQUESTS_TIMEOUT, *args, **kwargs)
            except self.retryable as err:
                raise NetworkRetryableError(
                    'A network error caused the failure of the job: '
                    '%s' % err)
        if self.debug:
            def with_debug(*args, **kwargs):
                kwargs['verify'] = False
                return with_auth(*args, **kwargs)
            return with_debug
        return with_auth


class QoQaAdapter(CRUDAdapter):
    """ External Records Adapter for QoQa """

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

    def url(self, with_lang=False):
        values = {'url': self.client.base_url,
                  'version': self.version,
                  'lang': '',
                  'endpoint': self._endpoint,
                  }
        if with_lang:
            values['lang'] = '/' + self.lang
        return "{url}api/{version}{lang}/{endpoint}/".format(**values)

    def _handle_response(self, response):
        _logger.debug("%s %s returned %s %s", response.request.method,
                      response.url, response.status_code, response.reason)
        if response.request.method == 'POST':
            _logger.debug("The POST body was: %s", response.request.body)
        if response.status_code == 403:
            msg = ("The call '%(method)s %(url)s' could not be completed "
                   "due to: %(reason)s. Check the OAuth tokens and "
                   "the permissions on %(base_url)spermission/")
            vals = {'method': response.request.method,
                    'url': response.url,
                    'reason': response.reason,
                    'base_url': self.client.base_url,
                    }
            raise QoQaAPISecurityError(msg % vals)
        # Server error : retry later
        if response.status_code in (500, 502, 504):
            raise NetworkRetryableError(
                'A HTTP server error caused the failure of the job: '
                'HTTP %s %s' % (response.status_code, response.reason))
        response.raise_for_status()
        try:
            parsed = json.loads(response.content)
        except ValueError as err:
            req = "%s %s with content:\n%s\n\nReturned %s %s:\n%s" % (
                response.request.method,
                response.url,
                response.request.body,
                response.status_code,
                response.reason,
                response.content,
            )
            msg = "%s\n\n%s" % (err, req)
            raise QoQaResponseNotParsable(msg)
        if parsed.get('errors'):
            _logger.error("%s %s with content:\n%s\n\nReturned %s %s:\n%s",
                          response.request.method,
                          response.url,
                          response.request.body,
                          response.status_code,
                          response.reason,
                          response.content)
            errors = []
            for err in parsed['errors']:
                message = err['message']
                if err.get('extras'):
                    message += err['extras']
                errors.append((err['type'], err['code'], message))
            raise QoQaResponseError(errors)
        return parsed

    def create(self, vals):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        vals = {self._endpoint: vals}
        response = self.client.post(url, data=json.dumps(vals),
                                    headers=headers)
        result = self._handle_response(response)
        assert result['data']['id']
        return result['data']['id']

    def write(self, id, vals):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        vals = {self._endpoint: vals}
        response = self.client.put(url + str(id),
                                   data=json.dumps(vals),
                                   headers=headers)
        self._handle_response(response)

    def read(self, id):
        url = "{0}{1}".format(self.url(), id)
        response = self.client.get(url)
        result = self._handle_response(response)
        return result['data']

    def search(self, filters=None, from_date=None, to_date=None):
        url = self.url()
        payload = {}
        if from_date is not None:
            payload['timestamp_from'] = from_date
        if to_date is not None:
            payload['timestamp_to'] = to_date
        if filters is not None:
            payload.update(filters)
        response = self.client.get(url, params=payload)
        records = self._handle_response(response)
        return [r['id'] for r in records['data']]
