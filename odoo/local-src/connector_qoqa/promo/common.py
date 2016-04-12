# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


@qoqa
class QoQaPromo(QoQaAdapter):
    _model_name = 'qoqa.promo'
    _endpoint = 'promo'


class QoqaPromoType(models.Model):
    """ Promo types on QoQa.

    Allow to configure the accounting journals and products for
    the promotions.

    Promos are:

        1 Customer service
        2 Marketing
        3 Affiliation
        4 Staff
        5 Mailing

    """
    _name = 'qoqa.promo.type'
    _inherit = 'qoqa.binding'
    _description = 'QoQa Promo Type'

    name = fields.Char()
    property_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain="[('type', '=', 'general')]",
        company_dependent=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )


@qoqa
class PromoTypeBinder(QoQaDirectBinder):
    _model_name = 'qoqa.promo.type'

    def bind(self, external_id, binding_id):
        """ Company are not synchronized, raise an error """
        raise TypeError('Promo Types are not synchronized, thus, bind() '
                        'is not applicable')
