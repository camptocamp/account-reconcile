# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple

import mock

from freezegun import freeze_time

from openerp.addons.connector.tests.common import mock_job_delay_to_direct

from openerp.addons.connector_qoqa.unit.importer import import_record

from .common import recorder, QoQaTransactionCase

ExpectedOffer = namedtuple(
    'ExpectedOffer',
    'name qoqa_link qoqa_edit_link'
)


class TestImportOffer(QoQaTransactionCase):
    """ Test the import of offers from QoQa """

    def setUp(self):
        super(TestImportOffer, self).setUp()
        self.Offer = self.env['qoqa.offer']
        self.setup_company()
        self.sync_metadata()

    @freeze_time('2016-04-20 00:00:00')
    def test_import_offer_batch(self):
        from_date = '2016-04-01 00:00:00'
        self.backend_record.import_offer_from_date = from_date
        batch_job_path = ('openerp.addons.connector_qoqa.unit'
                          '.importer.import_batch')
        record_job_path = ('openerp.addons.connector_qoqa.unit'
                           '.importer.import_record')
        # execute the batch job directly and replace the record import
        # by a mock (individual import is tested elsewhere)
        with recorder.use_cassette('test_import_offer_batch') as cassette, \
                mock_job_delay_to_direct(batch_job_path), \
                mock.patch(record_job_path) as import_record_mock:
            self.backend_record.import_offer()

            self.assertEqual(len(cassette.requests), 3)
            self.assertEqual(import_record_mock.delay.call_count, 9)

    @freeze_time('2016-04-20 00:00:00')
    @recorder.use_cassette()
    def test_import_offer(self):
        """ Import an Offer """
        import_record(self.session, 'qoqa.offer',
                      self.backend_record.id, 1)
        domain = [('qoqa_id', '=', '1')]
        offer = self.Offer.search(domain)
        offer.ensure_one()

        url = ('http://wwwqoqach-sprint.qoqa.com/'
               'fr/offer/view/1?show_banner=False')
        edit_url = self.backend_record.url + '/dot/edit/1'
        expected = [
            ExpectedOffer(
                name='Apple iPhone 6 / 64GB',
                qoqa_link=url,
                qoqa_edit_link=edit_url,
            ),
        ]
        self.assert_records(expected, offer)
