# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple

import mock

from freezegun import freeze_time

from openerp.addons.connector.tests.common import mock_job_delay_to_direct
from openerp.addons.connector_qoqa.unit.importer import import_record

from .common import recorder, QoQaTransactionCase

ExpectedPartner = namedtuple(
    'ExpectedPartner',
    'name qoqa_name email created_at updated_at lang'
)
ExpectedAddress = namedtuple(
    'ExpectedAddress',
    'name street street2 city zip country_id lang parent_id '
    'phone digicode created_at updated_at'
)


class TestImportPartner(QoQaTransactionCase):
    """ Test the import of partner from QoQa.  """

    def setUp(self):
        super(TestImportPartner, self).setUp()
        self.QoqaPartner = self.env['qoqa.res.partner']
        self.Partner = self.env['res.partner']
        self.QoqaAddress = self.env['qoqa.address']
        self.setup_company()
        self.sync_metadata()

    @freeze_time('2016-04-20 00:00:00')
    def test_import_partner_batch(self):
        from_date = '2016-04-01 00:00:00'
        self.backend_record.import_res_partner_from_date = from_date
        batch_job_path = ('openerp.addons.connector_qoqa.unit'
                          '.importer.import_batch')
        record_job_path = ('openerp.addons.connector_qoqa.unit'
                           '.importer.import_record')
        # execute the batch job directly and replace the record import
        # by a mock (individual import is tested elsewhere)
        with recorder.use_cassette('test_import_partner_batch') as cassette, \
                mock_job_delay_to_direct(batch_job_path), \
                mock.patch(record_job_path) as import_record_mock:
            self.backend_record.import_res_partner()

            self.assertEqual(len(cassette.requests), 3)
            self.assertEqual(import_record_mock.delay.call_count, 8)

    @freeze_time('2016-04-20 00:00:00')
    def test_import_partner_record(self):
        """ Import a batch of partners (QoQa users) """
        with recorder.use_cassette('test_import_partner_record_1000006'):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_record.id, 1000006)
        domain = [('qoqa_id', '=', '1000006')]
        partner_bindings = self.QoqaPartner.search(domain)
        partner_bindings.ensure_one()

        expected = [
            ExpectedPartner(
                name='QoQasien (qoqasien@qoqa.com)',
                qoqa_name='QoQasien',
                email='qoqasien@qoqa.com',
                created_at='2016-04-19 12:02:11',
                updated_at='2016-04-19 12:02:11',
                lang='fr_FR'
            )]

        self.assert_records(expected, partner_bindings)

    @freeze_time('2016-04-20 00:00:00')
    def test_import_partner_twice(self):
        """ Import a partner twice, the second import is skipped"""
        with recorder.use_cassette('test_import_partner_record_1000006'):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_record.id, 1000006)
        domain = [('qoqa_id', '=', '1000006')]
        partner_binding = self.QoqaPartner.search(domain)
        partner_binding.ensure_one()
        sync_date1 = partner_binding.sync_date

        with recorder.use_cassette('test_import_partner_record_1000006'):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_record.id, 1000006)

        partner_binding2 = self.QoqaPartner.search(domain)
        sync_date2 = partner_binding2.sync_date
        self.assertEquals(partner_binding, partner_binding2)
        self.assertEquals(sync_date1, sync_date2)

    @freeze_time('2016-04-20 00:00:00')
    def test_import_address_batch(self):
        from_date = '2016-04-01 00:00:00'
        self.backend_record.import_address_from_date = from_date
        batch_job_path = ('openerp.addons.connector_qoqa.unit'
                          '.importer.import_batch')
        record_job_path = ('openerp.addons.connector_qoqa.unit'
                           '.importer.import_record')
        # execute the batch job directly and replace the record import
        # by a mock (individual import is tested elsewhere)
        with recorder.use_cassette('test_import_address_batch') as cassette, \
                mock_job_delay_to_direct(batch_job_path), \
                mock.patch(record_job_path) as import_record_mock:
            self.backend_record.import_address()

            self.assertEqual(len(cassette.requests), 3)
            self.assertEqual(import_record_mock.delay.call_count, 10)

    @freeze_time('2016-04-20 00:00:00')
    def test_import_address_record(self):
        """ Import an address """
        with recorder.use_cassette('test_import_address_record'):
            import_record(self.session, 'qoqa.address',
                          self.backend_record.id, 100000001)
        domain = [('qoqa_id', '=', '100000001')]
        address_binding = self.QoqaAddress.search(domain)
        address_binding.ensure_one()

        partner_domain = [('qoqa_id', '=', '1000003')]
        partner_binding = self.QoqaPartner.search(partner_domain)
        partner_binding.ensure_one()
        # we write something on the partner just to ensure that the parent and
        # the address do not share the same values (as it happens when an
        # address is of type 'contact'
        partner_binding.street = 'Another street'
        partner_binding.city = 'Another city'

        expected = [
            ExpectedAddress(
                name='John Doe',
                street='Chemin du bois 17',
                street2=False,
                city='Hauterive',
                zip='2068',
                country_id=self.env.ref('base.ch'),
                lang='de_DE',
                parent_id=partner_binding.openerp_id,
                phone='0781733455',
                digicode=False,
                created_at='2016-05-11 09:44:21',
                updated_at='2016-05-11 09:44:21',
            ),
        ]
        self.assert_records(expected, address_binding)
