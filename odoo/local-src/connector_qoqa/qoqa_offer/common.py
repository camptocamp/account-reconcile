# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, exceptions, _

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaOffer(models.Model):
    _inherit = 'qoqa.offer'

    backend_id = fields.Many2one(
        related='qoqa_shop_id.backend_id',
        string='QoQa Backend',
        readonly=True,
    )
    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)
    qoqa_sync_date = fields.Datetime(
        string='Last synchronization date',
        copy=False,
    )
    qoqa_link = fields.Char(
        compute='_compute_qoqa_link',
        string='Link',
    )
    qoqa_edit_link = fields.Char(
        compute='_compute_qoqa_edit_link',
        string='Edit Offer Content',
    )

    _sql_constraints = [
        ('qoqa_uniq', 'unique(qoqa_id)',
         "An offer with the same ID on QoQa already exists"),
    ]

    @api.depends()
    def _compute_qoqa_link(self):
        url_template = "{base_url}/{lang}/offers/{qoqa_id}"
        for record in self:
            if not record.qoqa_id:
                continue
            if self.env.context.get('lang'):
                lang = self.env.context['lang'][:2]
            else:
                lang = 'fr'
            base_url = record.qoqa_shop_id.domain or record.backend_id.site_url
            if not base_url:
                continue
            if not base_url.startswith('http'):
                base_url = 'https://' + base_url
            values = {
                'base_url': base_url,
                'lang': lang,
                'qoqa_id': record.qoqa_id,
            }
            url = url_template.format(**values)
            record.qoqa_link = url

    @api.depends()
    def _compute_qoqa_edit_link(self):
        url_template = "{url}/admin/offers/{qoqa_id}/wizard?step=1"
        for record in self:
            if not record.qoqa_id:
                continue
            if not record.backend_id.site_url:
                continue
            values = {
                'url': record.backend_id.site_url,
                'qoqa_id': record.qoqa_id,
            }
            url = url_template.format(**values)
            record.qoqa_edit_link = url

    @api.multi
    def button_edit_offer_content(self):
        self.ensure_one()
        url = self.qoqa_edit_link
        if not url:
            raise exceptions.UserError(
                _('The offer does not exist on the backend.')
            )
        action = {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }
        return action

    @api.multi
    def unlink(self):
        exported = [offer for offer in self if offer.qoqa_id]
        if exported:
            raise exceptions.UserError(
                _('Exported Offers can no longer be deleted (ref: %s).'
                  'They can still be deactivated using the "active" '
                  'checkbox.') % ','.join(offer.name for offer in exported))
        return super(QoqaOffer, self).unlink()


@qoqa
class OfferAdapter(QoQaAdapter):
    _model_name = 'qoqa.offer'
    _endpoint = 'admin/offers'
    _resource = 'offer'
