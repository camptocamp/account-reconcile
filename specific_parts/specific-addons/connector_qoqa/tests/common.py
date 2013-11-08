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

import mock
from contextlib import contextmanager
from functools import partial
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


def get_qoqa_response(responses, url, *args, **kwargs):
    if not url in responses:
        raise Exception('Unhandled request: %s %s' % ('GET', url))
    response = mock.Mock()
    response.content = responses[url]
    response.status_code = 200
    response.reason = 'OK'
    response.url = url
    response.request.method = 'GET'
    return response


@contextmanager
def mock_api_responses(*responses):
    """
    :param responses: responses returned by QoQa
    :type responses: dict
    """
    all_responses = dict((k, v) for response in responses
                         for k, v in response.iteritems())
    with mock.patch('requests.get') as mock_get:
        mock_get.side_effect = partial(get_qoqa_response, all_responses)
        yield


class QoQaTransactionCase(common.TransactionCase):
    """ Base class for Tests with the QoQa backend """

    def setUp(self):
        super(QoQaTransactionCase, self).setUp()
        cr, uid = self.cr, self.uid
        backend_model = self.registry('qoqa.backend')
        self.session = ConnectorSession(cr, uid)
        self.backend_id = self.ref('connector_qoqa.qoqa_backend_config')
        fr_ids = self.registry('res.lang').search(
            cr, uid, [('code', '=', 'fr_FR')])
        fr_id = fr_ids[0]
        # ensure we use the tested version, otherwise the response
        # of the test data would not be found
        vals = {'version': 'v1',
                'url': 'http://admin.test02.qoqa.com',
                'default_lang_id': fr_id,
                }
        backend_model.write(cr, uid, self.backend_id, vals)
