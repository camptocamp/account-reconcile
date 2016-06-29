# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from collections import namedtuple

from .common import recorder, QoQaTransactionCase
from ..unit.importer import import_batch


ExpectedShop = namedtuple('ExpectedShop',
                          'name identifier domain company_id backend_id')


class TestImportMetadata(QoQaTransactionCase):
    """ Test the import of metadata from QoQa (actually
    QoQa Shops).
    """

    def setUp(self):
        super(TestImportMetadata, self).setUp()
        # create a new company so we'll check if the shop is linked
        # with the correct one when it is not the default one
        self.setup_company()
        self.QoqaShop = self.env['qoqa.shop']

    @recorder.use_cassette
    def test_import_shop(self):
        """ Import a Shop """
        import_batch(self.session, 'qoqa.shop', self.backend_record.id)

        shops = self.QoqaShop.search([])
        self.assertEqual(len(shops), 5)

        expected = [
            ExpectedShop(
                name='QoQa',
                identifier='wwwqoqach',
                domain='wwwqoqach-sprint.qoqa.com',
                company_id=self.company_ch,
                backend_id=self.backend_record
            ),
            ExpectedShop(
                name='Qwine',
                identifier='qwineqoqach',
                domain='qwineqoqach-sprint.qoqa.com',
                company_id=self.company_ch,
                backend_id=self.backend_record
            ),
            ExpectedShop(
                name='Qooking',
                identifier='qookingqoqach',
                domain='qookingqoqach-sprint.qoqa.com',
                company_id=self.company_ch,
                backend_id=self.backend_record
            ),
            ExpectedShop(
                name='QSport',
                identifier='qsportqoqach',
                domain='qsportqoqach-sprint.qoqa.com',
                company_id=self.company_ch,
                backend_id=self.backend_record
            ),
            ExpectedShop(
                name='QoQa France',
                identifier='wwwqoqafr',
                domain='wwwqoqafr-sprint.qoqa.com',
                company_id=self.company_fr,
                backend_id=self.backend_record
            ),
        ]
        self.assert_records(expected, shops)
