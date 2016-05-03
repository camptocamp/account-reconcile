# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from __future__ import division

from datetime import timedelta

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp

# TODO: review what fields are required


class QoqaOfferPositionVariant(models.Model):
    _name = 'qoqa.offer.position.variant'
    _description = 'QoQa Offer Position Variant'
    _order = 'sequence asc, id asc'

    sequence = fields.Integer('Sequence', default=1)
    position_id = fields.Many2one(
        comodel_name='qoqa.offer.position',
        string='Position',
        readonly=True,
        select=True,
        required=True,
        ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        select=True,
        ondelete='restrict')
    quantity = fields.Integer('Quantity', required=True)


class QoqaOfferPosition(models.Model):
    _name = 'qoqa.offer.position'
    _description = 'QoQa Offer Position'
    _order = 'sequence asc'

    REGULAR_PRICE_TYPE = [('normal', 'Normal Price'),
                          ('no_price', 'No Price'),
                          ('direct', 'Direct Price'),
                          ]

    offer_id = fields.Many2one(
        comodel_name='qoqa.offer',
        string='Offer',
        readonly=True,
        select=True,
        required=True,
    )
    variant_ids = fields.One2many(
        comodel_name='qoqa.offer.position.variant',
        inverse_name='position_id',
        string='Variants',
    )
    image_small = fields.Binary(
        compute='_compute_images',
        string='Thumbnail',
        readonly=True,
    )
    image_medium = fields.Binary(
        compute='_compute_images',
        string='Medium-sized Image',
        readonly=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        help="The first position is the main one",
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
    )
    currency_id = fields.Many2one(
        related='offer_id.pricelist_id.currency_id',
        type='many2one',
        string='Currency',
        readonly=True,
    )
    highlights = fields.Text(
        string='Highlights',
        readonly=True,
        translate=True,
    )
    description = fields.Html(
        string='Description',
        readonly=True,
        translate=True,
    )
    # only 1 tax is used on the QoQa backend, so we
    # have to choose only 1 for the position, the field
    # will also keep the reference to the historical tax
    # if the product's taxes change
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Tax',
        required=True,
        domain=[('type_tax_use', 'in', ('sale', 'all')),
                ('ecotax', '=', False)],
    )
    lot_size = fields.Integer(
        string='Lot Size',
        required=True,
    )
    max_sellable = fields.Integer(
        string='Max Sellable',
        required=True,
    )
    current_unit_price = fields.Float(
        related='product_tmpl_id.list_price',
        string="Product Price at Date",
        help="The price of the product at the beginning date of the "
             "offer. It will be modified directly on the product.",
        digits_compute=dp.get_precision('Product Price'),
    )
    unit_price = fields.Float(
        string='Unit Price',
        digits_compute=dp.get_precision('Product Price'),
        readonly=True,
    )
    lot_price = fields.Float(
        string='Lot Price',
        digits=(16, 2),
        readonly=True,
    )
    installment_price = fields.Float(
        string='Installment Price',
        digits_compute=dp.get_precision('Product Price'),
        readonly=True,
    )
    regular_price = fields.Float(
        string='Regular Price',
        digits_compute=dp.get_precision('Product Price'),
        required=True,
    )
    regular_price_type = fields.Selection(
        selection=REGULAR_PRICE_TYPE,
        string='Regular Price Type',
        required=True,
        default='normal',
    )
    buy_price = fields.Float(
        string='Buy Price',
        digits_compute=dp.get_precision('Product Price'),
    )
    top_price = fields.Float(
        string='Top Price',
        digits_compute=dp.get_precision('Product Price'),
    )
    date_delivery = fields.Date(
        string='Delivery Date',
        help="Maximum delivery date for customer. This information is "
             "displayed in the customer account",
    )
    booking_delivery = fields.Boolean(string='Booking Delivery')
    buyphrase_id = fields.Many2one(comodel_name='qoqa.buyphrase',
                                   string='Buyphrase')
    order_url = fields.Char(string='Order URL')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('variant_ids.product_id.image_small',
                 'variant_ids.product_id.image_medium')
    def _compute_images(self):
        for position in self:
            for variant in position.variant_ids:
                product = variant.product_id
                if product.image_small:
                    position.image_small = product.image_small
                    position.image_medium = product.image_medium
                break

    @api.multi
    def _history_price_date(self, offer):
        begin = fields.Date.from_string(offer.date_begin)
        begin += timedelta(hours=offer.time_begin)
        return fields.Datetime.to_string(begin)

    @api.model
    def create(self, vals):
        price = vals.get('current_unit_price') or 0
        lot_size = vals.get('lot_size') or 1
        vals = vals.copy()
        vals.update({
            'unit_price': price,
            'lot_price': price * lot_size,
        })
        if vals.get('offer_id'):
            offer_model = self.env['qoqa.offer']
            offer = offer_model.browse(vals['offer_id'])
            context = dict(self.env.context,
                           to_date=self._history_price_date(offer))
            self_c = self.with_context(context)
            _super = super(QoqaOfferPosition, self_c)
        else:
            _super = super(QoqaOfferPosition, self)
        res = _super.create(vals)

        # workaround: the related does not write the new price
        # on the product template when we create the record, so
        # do it manually
        # TODO: probably fixed, and maybe no longer required
        if 'current_unit_price' in vals:
            template_model = self.env['product.template']
            template = template_model.browse(vals['product_tmpl_id'])
            template.write({'list_price': price})
        # TODO: probably to remove:
        if vals.get('date_delivery'):
            self.check_date(vals['date_delivery'])
        return res

    @api.model
    def check_date(self, current_date):
        context_today = fields.Date.context_today(self)
        if current_date < context_today:
            raise exceptions.UserError(
                _('You cannot select a delivery date in the past')
            )
        else:
            return True

    @api.multi
    def write(self, vals):
        # TODO: probably to remove:
        if vals.get('date_delivery'):
            # We will check that the delivery date is not in the pas
            for position in self:
                self.check_date(vals['date_delivery'])

        # TODO: probably to remove
        if 'current_unit_price' in vals or 'lot_size' in vals:
            for position in self:
                offer_model = self.env['qoqa.offer']
                if vals.get('offer_id'):
                    offer = offer_model.browse(vals['offer_id'])
                else:
                    offer = position.offer_id

                context = dict(self.env.context,
                               to_date=self._history_price_date(offer))
                position = position.with_context(context)

                if 'current_unit_price' in vals:
                    price = vals['current_unit_price']
                else:
                    price = position.current_unit_price
                if 'lot_size' in vals:
                    lot_size = vals['lot_size']
                else:
                    lot_size = position.lot_size
                local_vals = vals.copy()
                local_vals.update({
                    'unit_price': price,
                    'lot_price': price * lot_size
                })
                super(QoqaOfferPosition, position).write(local_vals)
            return True
        else:
            return super(QoqaOfferPosition, self).write(vals)
