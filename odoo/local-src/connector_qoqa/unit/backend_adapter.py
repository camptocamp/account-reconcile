# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json
import logging
import requests
from requests.exceptions import HTTPError, RequestException, ConnectionError
from contextlib import contextmanager
from openerp import exceptions, _
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from openerp.addons.connector.exception import NetworkRetryableError
from ..exception import (QoQaResponseNotParsable,
                         QoQaAPIAuthError,
                         QoQaResponseError,
                         QoQaRecordDoesNotExist,
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
def api_handle_errors(message=u''):
    """ Handle error when calling the API

    It is meant to be used when a model does a direct
    call to a job using the API (not using job.delay()).
    Avoid to have unhandled errors raising on front of the user,
    instead, they are presented as :class:`openerp.exceptions.UserError`.
    """
    if message:
        message = message + u'\n\n'
    try:
        yield
    except NetworkRetryableError as err:
        raise exceptions.UserError(
            _(u'{}Network Error:\n\n{}').format(message, err)
        )
    except (HTTPError, RequestException, ConnectionError) as err:
        raise exceptions.UserError(
            _(u'{}API / Network Error:\n\n{}').format(message, err)
        )
    except QoQaAPIAuthError as err:
        raise exceptions.UserError(
            _(u'{}Authentication Error:\n\n{}').format(message, err)
        )
    except QoQaResponseError as err:
        raise exceptions.UserError(
            _(u'{}Error(s) returned by QoQa:\n\n{}').format(message,
                                                            unicode(err))
        )
    except QoQaResponseNotParsable:
        # The response from the backend cannot be parsed, not a
        # JSON.  So we don't know what the error is.
        _logger.exception(message)
        raise exceptions.UserError(
                _(u'{}Unknown Error').format(message)
        )


class QoQaClient(object):

    retryable = (requests.exceptions.Timeout,
                 requests.exceptions.ConnectionError,
                 )

    def __init__(self, base_url, token=False, debug=False):
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.debug = debug
        self._session = requests.Session()
        self._session.headers['Content-Type'] = 'application/json'
        self._session.headers['Accept'] = 'application/json'
        self.token = token

    @property
    def token(self):
        return self._token

    @token.setter  # noqa: ignore=W806 (wrong pyflakes warning)
    def token(self, value):
        if value:
            self._session.headers['Authorization'] = (
                'Token token="{}"'.format(value)
            )
        else:
            self._session.headers['Authorization'] = None
        self._token = value

    def __getattr__(self, attr):
        """ Forward attributes to ``requests``.

        This allows to call a ``post`` or ``get`` directly
        on a ``QoQaClient`` instance.

        It automatically adds the token in the Authorization header to
        all the requests.

        When the debug mode is activated, it disables the check
        on the SSL certificate.
        """
        dispatch = getattr(self._session, attr)

        def do_call(*args, **kwargs):
            kwargs.setdefault('allow_redirects', False)
            try:
                return dispatch(timeout=REQUESTS_TIMEOUT, *args, **kwargs)
            except self.retryable as err:
                raise NetworkRetryableError(
                    'A network error caused the failure of the job: '
                    '%s' % err)
        if self.debug:
            def with_debug(*args, **kwargs):
                kwargs['verify'] = False
                return do_call(*args, **kwargs)
            return with_debug
        return do_call


class QoQaAdapter(CRUDAdapter):
    """ External Records Adapter for QoQa

    The ``_endpoint`` and the ``_resource` are to define in the subclasses.
    They represent the following things in a call:
    ```
    POST https://baseurl/v1/<<_endpoint>>
     {"locale": "fr",
      "<<_resource>>": {"id": null, "name": "xyz"}}
    ```
    An example of endpoint is ``addresses` and of resource is ``address``.
    """

    _endpoint = None  # to define in subclasses, part of the url for a resource
    _resource = None  # to define in subclasses, name of the resource

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        assert self._endpoint, "_endpoint needs to be defined"
        super(QoQaAdapter, self).__init__(environment)
        backend = self.backend_record
        self.client = QoQaClient(backend.url,
                                 token=backend.token,
                                 debug=backend.debug)
        self.version = self.backend_record.version
        self.lang = self.env.context['lang'][:2]

    def url(self):
        values = {'url': self.client.base_url,
                  'version': self.version,
                  'endpoint': self._endpoint,
                  }
        return "{url}{version}/{endpoint}/".format(**values)

    def _parse_content(self, response):
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
        return parsed

    def _handle_response(self, response):
        _logger.debug("%s %s returned %s %s", response.request.method,
                      response.url, response.status_code, response.reason)
        if response.request.method == 'POST':
            _logger.debug("The POST body was: %s", response.request.body)
        if response.status_code in (401, 403):
            errors = []
            if response.content:
                parsed = self._parse_content(response)
                for err in parsed.get('errors', []):
                    errors.append((err['code'], err['title'], err['detail']))
            raise QoQaAPIAuthError(errors)
        # Server error : retry later
        if response.status_code in (500, 502, 504):
            raise NetworkRetryableError(
                'A HTTP server error caused the failure of the job: '
                'HTTP %s %s' % (response.status_code, response.reason))

        # When we request a new token with auth and the login/password is
        # wrong, the API returns a 302 redirect
        if response.is_redirect:
            raise QoQaAPIAuthError([])
        try:
            response.raise_for_status()
        except Exception:
            if response.content:
                # will raise an error with the content
                parsed = self._parse_content(response)
                _logger.error("%s %s with content:\n%s\n\nReturned %s %s:\n%s",
                              response.request.method,
                              response.url,
                              response.request.body,
                              response.status_code,
                              response.reason,
                              response.content.decode('utf-8'))
                errors = []
                for err in parsed.get('errors', []):
                    if err['code'] == 17:  # Maintenance
                        raise NetworkRetryableError(
                            'QoQa API is in maintenance mode',
                            seconds=60 * 3,
                            ignore_retry=True
                        )

                    errors.append((err['code'], err['title'], err['detail']))

                    if err['code'] == 2:  # Record does not exist
                        raise QoQaRecordDoesNotExist(errors)

                raise QoQaResponseError(errors)
            else:
                _logger.error(
                    u'bad status received on: %s %s %s',
                    response.request.method,
                    response.url,
                    response.request.body,
                )
            raise
        parsed = self._parse_content(response)
        return parsed

    def create(self, vals):
        assert self._resource, "_resource needs to be defined"
        url = self.url()
        vals = {self._resource: vals,
                'locale': self.lang}
        response = self.client.post(url, data=json.dumps(vals))
        result = self._handle_response(response)
        assert result['data']['id']
        return result['data']['id']

    def write(self, id, vals):
        assert self._resource, "_resource needs to be defined"
        url = self.url()
        vals = {self._resource: vals,
                'locale': self.lang}
        response = self.client.put(url + str(id),
                                   data=json.dumps(vals))
        self._handle_response(response)

    def read(self, id):
        url = "{0}{1}".format(self.url(), id)
        response = self.client.get(url)
        result = self._handle_response(response)
        return result

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

    def delete(self, id):
        url = "{0}{1}".format(self.url(), id)
        response = self.client.delete(url)
        result = self._handle_response(response)
        return result
