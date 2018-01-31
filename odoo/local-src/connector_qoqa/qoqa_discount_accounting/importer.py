# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from ..backend import qoqa

from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  ImportMapChild)
from openerp import fields
from ..connector import iso8601_to_utc_datetime
from ..unit.importer import QoQaImporter, DelayedBatchImporter
from ..unit.mapper import FromAttributes, FromDataAttributes
from ..exception import QoQaError
from ..unit.mapper import iso8601_to_utc


def _extract_lines_from_group(record):
    lines = [item for item in record['included']
             if item['type'] == 'discount_accounting_line']
    return lines


def _extract_discount_from_group(record):
    lines = [item for item in record['included']
             if item['type'] == 'discount']
    assert len(lines) == 1
    return lines[0]


@qoqa
class DiscountAccountingBatchImporter(DelayedBatchImporter):
    """ Import the QoQa Discount Accounting.

    For every discount's id in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.discount.accounting'


@qoqa
class QoQaDiscountAccountingImporter(QoQaImporter):
    _model_name = 'qoqa.discount.accounting'

    def _import(self, binding_id):
        """ Use the user from the shop's company for the import

        Allowing the records rules to be applied.

        """
        company_binder = self.binder_for('res.company')
        discount = _extract_discount_from_group(self.qoqa_record)
        qoqa_company_id = discount['attributes']['company_id']
        company_binding = company_binder.to_openerp(qoqa_company_id)
        user = company_binding.connector_user_id
        if not user:
            raise QoQaError('No connector user configured for company %s' %
                            company_binding.name)
        with self.session.change_user(user.id):
            super(QoQaDiscountAccountingImporter, self)._import(binding_id)

    def must_skip(self):
        """ Returns a reason if the import should be skipped.

        Returns None to continue with the import

        """
        assert self.qoqa_record
        lines = _extract_lines_from_group(self.qoqa_record)
        # 1 line is a voucher, we don't need them anymore (BIZ-711, BIZ-712)
        # so skip them
        if len(lines) == 1:
            return True

    def _is_uptodate(self, binding_id):
        # already imported, skip it (unless if `force` is used)
        assert self.qoqa_record
        if self.binder.to_openerp(self.qoqa_id):
            return True

    def _import_dependencies(self):
        """ Import the dependencies for the record """
        assert self.qoqa_record
        rec = self.qoqa_record
        user_id = rec['data']['attributes']['user_id']
        self._import_dependency(user_id, 'qoqa.res.partner')

    def _create_context(self):
        ctx = super(QoQaDiscountAccountingImporter, self)._create_context()
        ctx['check_move_validity'] = False  # checked in _create
        return ctx

    def _create(self, data):
        binding = super(QoQaDiscountAccountingImporter, self)._create(data)
        binding.openerp_id._post_validate()
        return binding


class BaseAccountingImportMapper(ImportMapper, FromDataAttributes):
    _model_name = None

    def _specific_move_values(self, record):
        """ Values of the moves which depend on the promo

        :return: browse_record of journal, ref

        """
        raise NotImplementedError

    @mapping
    def move_values(self, record):
        journal, ref = self._specific_move_values(record)
        attributes = record['data']['attributes']
        parsed = iso8601_to_utc_datetime(attributes['created_at'])
        date = fields.Date.to_string(parsed)
        company = self._company(record)
        vals = {
            'journal_id': journal.id,
            'company_id': company.id,
            'date': date,
            'ref': ref,
        }
        return vals

    def _company(self, record):
        company_binder = self.binder_for('res.company')
        discount = _extract_discount_from_group(record)
        qoqa_company_id = discount['attributes']['company_id']
        company = company_binder.to_openerp(qoqa_company_id)
        assert company
        return company

    def _partner(self, map_record):
        # Partner can be empty; if that's the case, return False
        attributes = map_record.source['data']['attributes']
        qoqa_user_id = attributes['user_id']
        if not qoqa_user_id:
            return self.env['res.partner'].browse()
        else:
            binder = self.binder_for('qoqa.res.partner')
            partner = binder.to_openerp(qoqa_user_id, unwrap=True)
            assert partner, \
                "user_id should have been " \
                "imported in import_dependencies"
            return partner

    def _currency(self, map_record, company):
        binder = self.binder_for('res.currency')
        discount = _extract_discount_from_group(map_record.source)
        qoqa_currency_id = discount['attributes']['currency']
        currency = binder.to_openerp(qoqa_currency_id)
        assert currency
        if currency != company.currency_id:
            return currency

    def _analytic_account(self, map_record):
        discount = _extract_discount_from_group(map_record.source)
        qoqa_website_id = discount['attributes']['accounting_website_id']
        binder = self.binder_for('qoqa.shop')
        shop = binder.to_openerp(qoqa_website_id, unwrap=True)
        assert shop, "Unknow shop_id, refresh the Backend's metadata"
        return shop.analytic_account_id

    def _payment_id(self, map_record):
        discount = _extract_discount_from_group(map_record)
        return discount['attributes'].get('payment_id')

    def _line_options(self, map_record, values):
        options = self.options.copy()
        company = self._company(map_record.source)
        journal_id = values['journal_id']
        payment_id = self._payment_id(map_record.source)
        options.update({
            'journal': self.env['account.journal'].browse(journal_id),
            'partner': self._partner(map_record),
            'company': company,
            'date': values['date'],
            'analytic_account': self._analytic_account(map_record),
            'ref': values['ref'],
            'qoqa_payment_id': payment_id,
        })
        currency = self._currency(map_record, company)
        if currency:
            options['currency'] = currency
        return options


@qoqa
class PromoDiscountAccountingMapper(BaseAccountingImportMapper):
    _model_name = 'qoqa.discount.accounting'

    from_data_attributes = [(iso8601_to_utc('created_at'), 'created_at'),
                            (iso8601_to_utc('updated_at'), 'updated_at'),
                            ]

    def _get_map_child_unit(self, model_name):
        return self.unit_for(PromoDiscountAccountingLineMapChild,
                             model='qoqa.discount.accounting.line')

    def _specific_move_values(self, record):
        """ Values of the moves which depend on the promo / vouchers

        :return: browse_record of journal, ref

        """
        discount = _extract_discount_from_group(record)
        promo_type = self._promo_type(discount)
        journal = promo_type.property_journal_id
        if not journal:
            user = self.env.user
            raise MappingError('No journal defined for the promo type "%s" '
                               'for company "%s".\n'
                               'Please configure it on the QoQa backend.' %
                               (promo_type.name, user.company_id.name))
        ref = unicode(discount['id'])
        return journal, ref

    def _promo_type(self, discount):
        promo_binder = self.binder_for('qoqa.promo.type')
        qpromo_type_id = discount['attributes']['sub_type']
        promo_type = promo_binder.to_openerp(qpromo_type_id)
        if not promo_type:
            raise MappingError("Type of promo %s is unknown. " %
                               (qpromo_type_id,))
        return promo_type

    def _product(self, map_record):
        discount = _extract_discount_from_group(map_record.source)
        promo_type = self._promo_type(discount)
        return promo_type.product_id

    @mapping
    def discount_type(self, record):
        return {'discount_type': 'promo'}

    def finalize(self, map_record, values):
        lines = _extract_lines_from_group(map_record.source)
        map_child = self._get_map_child_unit('qoqa.discount.accounting.line')
        options = self._line_options(map_record, values)
        options['product'] = self._product(map_record)
        items = map_child.get_items(lines, map_record,
                                    'qoqa_discount_accounting_line_ids',
                                    options=options)
        values['qoqa_discount_accounting_line_ids'] = items
        return values

    def _line_options(self, map_record, values):
        # Use the VAT line (always linked to the expense line)
        # to determine if the retrieved item is an issuance
        # or a cancellation.
        # Also, store in options the highest absolute amount,
        # to recompute tax amounts with higher precision.
        options = super(PromoDiscountAccountingMapper, self)._line_options(
            map_record, values)
        lines = _extract_lines_from_group(map_record.source)
        for line in lines:
            line_attrs = line['attributes']
            if line_attrs['is_vat']:
                options.update({
                    'is_cancellation': float(line_attrs['amount']) < 0
                })
                break
        if not options['is_cancellation']:
            options.update({
                'taxed_amount': min([float(line['attributes']['amount'])
                                     for line in lines])
            })
        else:
            options.update({
                'taxed_amount': max([float(line['attributes']['amount'])
                                     for line in lines])
            })
        return options


@qoqa
class PromoDiscountAccountingLineMapChild(ImportMapChild):
    _model_name = 'qoqa.discount.accounting.line'

    def _child_mapper(self):
        return self.unit_for(PromoDiscountAccountingLineMapper)

    def skip_item(self, map_record):
        """ Skip VAT entries since they are generated by Odoo """
        record = map_record.source
        if record['attributes']['is_vat']:
            return True
        if not float(record['attributes']['amount']):
            return True


class BaseLineMapper(ImportMapper, FromAttributes):

    direct = [
        ('id', 'qoqa_id'),
    ]

    from_attributes = [
        (iso8601_to_utc('created_at'), 'created_at'),
        (iso8601_to_utc('updated_at'), 'updated_at'),
        ('label', 'name'),
    ]

    @mapping
    def ref(self, record):
        # we need to write on the ref even if its a relatede to the move,
        # otherwise the creation of the tax line in AccountMoveLine.create()
        # sets a None value in the move's ref
        return {'ref': self.options.ref}

    @mapping
    def date(self, record):
        return {'date': self.options.date}

    @mapping
    def partner(self, record):
        return {'partner_id': self.options.partner.id}

    @mapping
    def currency(self, record):
        if self.options.currency_id:
            return {'currency_id': self.options.currency.id}

    @mapping
    def transaction_ref(self, record):
        if self.options.qoqa_payment_id:
            return {'transaction_ref': self.options.qoqa_payment_id}


@qoqa
class PromoDiscountAccountingLineMapper(BaseLineMapper):
    _model_name = 'qoqa.discount.accounting.line'

    # Method to determine if the line is the
    # "main" emission/cancellation line.
    def is_main_line(self, amount, is_cancellation):
        if amount < 0 and not is_cancellation:
            return True
        if amount > 0 and is_cancellation:
            return True
        return False

    @mapping
    def amount(self, record):
        amount = float(record['attributes']['amount'])
        if (not self.is_main_line(amount, self.options.is_cancellation) and
                self.options.taxed_amount):
            # Put inverse amount of emission/cancellation in expense.
            amount = -self.options.taxed_amount
        values = {
            'debit': amount if amount > 0 else 0,
            'credit': -amount if amount < 0 else 0,
        }
        return values

    @mapping
    def account(self, record):
        """ Return line's account.

        The account for credit is the product income account.
        The account for debit comes from the journal.

        """
        amount = float(record['attributes']['amount'])
        assert amount, \
            "lines without amount should be filtered " \
            "in DiscountAccountingLineMapChild"

        if self.is_main_line(amount, self.options.is_cancellation):
            # emission/cancellation line
            account = self.options.product.property_account_income_id
            if not account:
                raise MappingError('No Income Account configured '
                                   'on product %s' %
                                   (self.options.product.display_name,))
        else:
            # expense line
            account = self.options.journal.default_debit_account_id
            if not account:
                journal = self.options.journal
                raise MappingError('No Default Debit Account configured '
                                   'on journal [%s] %s' %
                                   (journal.code, journal.name))

        vals = {'account_id': account.id}
        if account.user_type_id.analytic_policy != 'never':
            vals['analytic_account_id'] = self.options.analytic_account.id
        return vals

    @mapping
    def taxes(self, record):
        """ Return the tax used by QoQa.

        QoQa provides a VAT also on the emission/cancellation line,
        but we want it only on the expense line. We also use the
        tax code to recompute the expense line's amount.

        """
        amount = float(record['attributes']['amount'])
        if self.is_main_line(amount, self.options.is_cancellation):
            return
        binder = self.binder_for('account.tax')
        tax = binder.to_openerp(record['attributes']['vat_id'])
        if not tax:
            raise MappingError('No known tax for qoqa vat_id: %s ' %
                               (record['attributes']['vat_id'],))
        result = {'tax_ids': [(6, 0, tax.ids)]}
        return result
