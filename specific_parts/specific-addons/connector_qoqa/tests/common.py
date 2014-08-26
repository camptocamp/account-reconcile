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

    def setUpCompany(self):
        """ When we import records linked with a Shop, we need to
        create a company for the test shop.

        Here is the boilerplate to create the company, assign
        the user, create a pricelist...

        """
        cr, uid = self.cr, self.uid
        company_obj = self.registry('res.company')
        # create a new company so we'll check if it shop is linked
        # with the correct one when it is not the default one
        connector_user_id = self.ref('connector_qoqa.user_connector_ch')
        vals = {'name': 'Qtest', 'qoqa_id': 42,
                'connector_user_id': connector_user_id}
        self.company_id = company_obj.create(cr, uid, vals)
        User = self.registry('res.users')
        User.write(cr, uid, [connector_user_id],
                   {'company_ids': [(4, self.company_id)],
                    'company_id': self.company_id})
        Pricelist = self.registry('product.pricelist')
        vals = {'company_id': self.company_id,
                'type': 'sale',
                'name': 'test',
                'currency_id': self.ref('base.CHF'),
                }
        self.pricelist_id = Pricelist.create(cr, uid, vals)
        PricelistVersion = self.registry('product.pricelist.version')
        vals = {'company_id': self.company_id,
                'name': 'test',
                'pricelist_id': self.pricelist_id,
                'qoqa_id': 99999999,
                }
        version_id = PricelistVersion.create(cr, uid, vals)

        PriceType = self.registry('product.price.type')
        vals = {'company_id': self.company_id,
                'field': 'list_price',
                'currency_id': self.ref('base.CHF'),
                'name': 'test',
                }
        pricetype_id = PriceType.create(cr, uid, vals)

        PricelistItem = self.registry('product.pricelist.item')
        vals = {'company_id': self.company_id,
                'name': 'test',
                'price_version_id': version_id,
                'base': pricetype_id,
                }
        PricelistItem.create(cr, uid, vals)

        vals = {'company_id': self.company_id,
                'name': 'test',
                'qoqa_id': 99999999,
                }
        PaymentMethod = self.registry('payment.method')
        self.payment_method_id = PaymentMethod.create(cr, uid, vals)


class MockResponseImage(object):
    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'image/jpeg'}

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code

    def close(self):
        pass
