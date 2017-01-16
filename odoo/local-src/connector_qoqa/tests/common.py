# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json
import urlparse

from collections import namedtuple
from os.path import dirname, exists, join

from vcr import VCR

import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


# secret.txt is a file which can be placed by the developer in the
# 'tests' directory. It contains the username in the first line at the
# password in the second. The secret.txt file must not be committed.
# The API username and password will be used to record the requests
# with vcr, but will not be stored in the fixtures files
#
# login and password are used for authentication tests (test_auth.py),
# token is used for all the other calls
#
# the login and password must be asked to QoQa / found in lastpass,
# the token can be generated using the authentication wizard
_Secrets = namedtuple('Secrets', 'login password token')
filename = join(dirname(__file__), 'secret.txt')
if exists(filename):
    with open(filename, 'r') as fp:
        assert len(fp.readlines()) == 3, "secret.txt must have 3 lines:" \
                "login, password, token"
        fp.seek(0)
        secrets = _Secrets(
            login=next(fp).strip(),
            password=next(fp).strip(),
            token=next(fp).strip()
        )
else:
    secrets = _Secrets('', '', '')


def scrub_login_request(request):
    if request.path == '/v1/auth/':
        body = json.loads(request.body)
        body['user']['login'] = 'xxxxxx'
        body['user']['password'] = 'xxxxxx'
        request.body = json.dumps(body)
    return request


def scrub_login_response(response):
    try:
        content = json.loads(response['body']['string'])
    except ValueError:
        return response
    data = content.get('data')
    if isinstance(data, dict):
        if data.get('attributes', {}).get('token'):
            content['data']['attributes']['token'] = 'xxxxxx'
        response['body']['string'] = json.dumps(content)
    return response


recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml'),
    filter_headers=['Authorization'],
    before_record=scrub_login_request,
    before_record_response=scrub_login_response,
)


class QoQaTransactionCase(common.TransactionCase):
    """ Base class for Tests with the QoQa backend """

    def setUp(self):
        super(QoQaTransactionCase, self).setUp()
        self.session = ConnectorSession.from_env(self.env)
        self.backend_record = self.env['qoqa.backend'].get_singleton()
        self.lang_fr = self.env['res.lang'].search([('code', '=', 'fr_FR')])
        self.lang_fr.ensure_one()
        # ensure we use the tested version, otherwise the response
        # of the test data would not be found
        vals = {'version': 'v1',
                'url': 'https://api-sprint.qoqa.com',
                'default_lang_id': self.lang_fr.id,
                'token': secrets.token,
                }
        self.backend_record.write(vals)
        self.setup_bindings()

        recorder.register_matcher('json_body', self.check_json_body)

    def setup_bindings(self):
        self.env.ref('base.ch').qoqa_id = 1

    def check_json_body(self, req1, req2):
        """ Check real request datas in addition to compare with cassette.

        By default, this matcher is only registered as 'json_body'.
        Need be added to recorder.match_on to be called.
        e.g:
            match_on = recorder.match_on + ('json_body',)
            with recorder.use_cassette(vcr_name, match_on=match_on):
               [....]
        """
        if req1.path != req2.path:
            return False

        return self._check_json_body(
            req1.path,
            json.loads(req1.body),
            json.loads(req2.body)
        )

    def _check_json_body(self, path, query_json, saved_json):
        """ Can be override.
        """
        return query_json == saved_json

    def assert_records(self, expected_records, records):
        """ Assert that a recordset matches with expected values.

        The expected records are a list of nametuple, the fields of the
        namedtuple must have the same name than the recordset's fields.

        The expected values are compared to the recordset and records that
        differ from the expected ones are show as ``-`` (missing) or ``+``
        (extra) lines.

        Example::

            ExpectedShop = namedtuple('ExpectedShop',
                                      'name company_id')
            expected = [
                ExpectedShop(
                    name='QoQa',
                    company_id=self.company_ch
                ),
                ExpectedShop(
                    name='Qwine',
                    company_id=self.company_ch
                ),
            ]
            self.assert_records(expected, shops)

        Possible output:

         - qoqa.shop(name: QoQa France, company_id: res.company(2,))
         - qoqa.shop(name: Qsport, company_id: res.company(1,))
         + qoqa.shop(name: QSport, company_id: res.company(1,))

        :param expected_records: list of namedtuple with matching values
                                 for the records
        :param records: the recordset to check
        :raises: AssertionError if the values do not match
        """
        model_name = records._model._name
        records = list(records)
        assert len(expected_records) > 0, "must have > 0 expected record"
        fields = expected_records[0]._fields
        not_found = []
        equals = []
        for expected in expected_records:
            for record in records:
                for field, value in expected._asdict().iteritems():
                    if not getattr(record, field) == value:
                        break
                else:
                    records.remove(record)
                    equals.append(record)
                    break
            else:
                not_found.append(expected)
        message = []
        for record in equals:
            # same records
            message.append(
                u' ✓ {}({})'.format(
                    model_name,
                    u', '.join(u'%s: %s' % (field, getattr(record, field)) for
                               field in fields)
                )
            )
        for expected in not_found:
            # missing records
            message.append(
                u' - {}({})'.format(
                    model_name,
                    u', '.join(u'%s: %s' % (k, v) for
                               k, v in expected._asdict().iteritems())
                )
            )
        for record in records:
            # extra records
            message.append(
                u' + {}({})'.format(
                    model_name,
                    u', '.join(u'%s: %s' % (field, getattr(record, field)) for
                               field in fields)
                )
            )
        if not_found or records:
            raise AssertionError(u'Records do not match:\n\n{}'.format(
                '\n'.join(message)
            ))

    def assert_cassette_record_exported(self, response, binding):
        response = json.loads(response['body']['string'])
        qoqa_id = response['data']['id']
        # cast to str because we store the external id as Char
        self.assertEqual(binding.qoqa_id, str(qoqa_id))

    def sync_metadata(self):
        with recorder.use_cassette('sync_metadata'):
            self.backend_record.synchronize_metadata()

    def setup_company(self):
        """ When we import records linked with a Shop, we need to
        create a company for the tested shop.

        Here is the boilerplate to create the company, assign
        the user, create a pricelist and a payment method.

        This helper can be called in the tests if needed

        """

        Company = self.env['res.company']

        connector_user_ch = self.env.ref('connector_qoqa.user_connector_ch')
        connector_user_fr = self.env.ref('connector_qoqa.user_connector_fr')

        self.company_ch = self.env.ref('base.main_company')
        self.company_ch.currency_id = self.env.ref('base.CHF')
        vals = {'name': 'QoQa CH',
                'qoqa_id': 1,
                'connector_user_id': connector_user_ch.id}
        self.company_ch.write(vals)
        vals = {'name': 'QoQa FR',
                'qoqa_id': 2,
                'currency_id': self.env.ref('base.EUR').id,
                'connector_user_id': connector_user_fr.id}
        self.company_fr = Company.create(vals)

        connector_user_ch.write({'company_ids': [(4, self.company_ch.id)],
                                 'company_id': self.company_ch.id})
        connector_user_fr.write({'company_ids': [(4, self.company_fr.id)],
                                 'company_id': self.company_fr.id})

        Pricelist = self.env['product.pricelist']
        vals = {'company_id': self.company_fr.id,
                'name': 'test',
                'currency_id': self.env.ref('base.EUR').id,
                }
        self.pricelist_fr = Pricelist.create(vals)

        PricelistItem = self.env['product.pricelist.item']
        vals = {'company_id': self.company_fr.id,
                'name': 'test',
                'pricelist_id': self.pricelist_fr.id,
                'base': 'list_price',
                }
        PricelistItem.create(vals)

    def create_binding_no_export(self, model_name, openerp_id, qoqa_id=None,
                                 **cols):
        values = {
            'backend_id': self.backend_record.id,
            'openerp_id': openerp_id,
            'qoqa_id': qoqa_id,
        }
        if cols:
            values.update(cols)
        return self.env[model_name].with_context(
            connector_no_export=True
        ).create(values)

    @staticmethod
    def parse_path(url):
        return urlparse.urlparse(url).path

    @staticmethod
    def parse_body(request):
        return json.loads(request.body)
