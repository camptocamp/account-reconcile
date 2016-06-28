# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from openerp.tools.safe_eval import safe_eval
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.importer import DelayedBatchImporter, QoQaImporter
from ..unit.mapper import FromDataAttributes, iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class CrmClaimBatchImporter(DelayedBatchImporter):
    """ Import the QoQa Users.

    For every id in in the list of claims, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.crm.claim'


@qoqa
class CrmClaimImporter(QoQaImporter):
    _model_name = 'qoqa.crm.claim'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        qoqa_user_id = rec['data']['attributes']['user_id']
        self._import_dependency(qoqa_user_id, 'qoqa.res.partner')

    def _after_import(self, binding):
        medium_importer = self.unit_for(QoQaImporter, 'qoqa.crm.claim.medium')
        if self.qoqa_record.get('included'):
            media = [item for item in self.qoqa_record['included']
                     if item['type'] == 'cs_claim_medium']
            for item in media:
                medium_importer.run(
                    item['id'],
                    record=item,
                    claim_binding=binding
                )


@qoqa
class CrmClaimImportMapper(ImportMapper, FromDataAttributes):
    _model_name = 'qoqa.crm.claim'

    from_data_attributes = [
        ('subject', 'name'),
        ('message', 'description'),
        ('email', 'email_from'),
        ('phone', 'partner_phone'),
        (iso8601_to_utc('created_at'), 'date'),
    ]

    @mapping
    def partner_id(self, record):
        user_id = record['data']['attributes']['user_id']
        binder = self.binder_for('qoqa.res.partner')
        return {'partner_id': binder.to_openerp(user_id, unwrap=True).id}

    @mapping
    def sale_and_invoice(self, record):
        binder = self.binder_for('qoqa.sale.order')
        qoqa_order_id = record['data']['attributes']['order_id']
        sale = binder.to_openerp(qoqa_order_id, unwrap=True)
        if not sale:
            return {}
        invoice = sale._last_invoice()
        return {'invoice_id': invoice.id}

    def finalize(self, map_record, values):

        if values.get('partner_id'):
            claim_model = self.env['crm.claim']
            onchange = claim_model.onchange_partner_id(values['partner_id'])
            for field, val in onchange['value'].iteritems():
                if not values.get(field) and val:
                    values[field] = val

        identifier = map_record.source['data']['attributes']['identifier']
        if identifier:
            email_alias = self.env['mail.alias'].search(
                [('alias_name', '=', identifier)],
                limit=1
            )
            if not email_alias:
                raise MappingError(
                    "Email alias '%s' not found" % identifier
                )
            default_values = safe_eval(email_alias.alias_defaults)
            default_values.update(values)
            values = default_values

        existing = self.env['crm.claim']
        if not self.options.for_create:
            existing = self.binder_for().to_openerp(
                map_record.source['data']['id'], unwrap=True,
            )

        # do not recreate the claim lines if we are updating an existing record
        if not existing.claim_line_ids:
            claim_model = self.env['crm.claim'].with_context(create_lines=True)
            virtual_claim = claim_model.new(values)
            virtual_claim._onchange_invoice_warehouse_type_date()
            values = virtual_claim._convert_to_write(virtual_claim._cache)
        return values


@qoqa
class CrmClaimMediumImporter(QoQaImporter):
    _model_name = 'qoqa.crm.claim.medium'

    def run(self, qoqa_id, force=False, record=None, claim_binding=None):
        self.claim_binding = claim_binding
        _super = super(CrmClaimMediumImporter, self)
        return _super.run(qoqa_id, force=force, record=record)

    def _update_data(self, map_record, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        _super = super(CrmClaimMediumImporter, self)
        return _super._update_data(map_record,
                                   claim_binding=self.claim_binding,
                                   **kwargs)

    def _create_data(self, map_record, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        _super = super(CrmClaimMediumImporter, self)
        return _super._create_data(map_record,
                                   claim_binding=self.claim_binding,
                                   **kwargs)


@qoqa
class CrmClaimMediumImportMapper(ImportMapper):
    _model_name = 'qoqa.crm.claim.medium'

    @mapping
    def all_values(self, record):
        attrs = record['attributes']
        url = attrs['file_url']
        values = {
            # TODO: at the moment, no name in API, improve that
            'name': url.split('/')[-1],
            'type': 'url',
            'url': url,
            'res_id': self.options.claim_binding.openerp_id.id,
            'res_model': 'crm.claim',
        }
        return values
