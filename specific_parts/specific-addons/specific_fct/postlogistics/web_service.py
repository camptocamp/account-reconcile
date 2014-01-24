# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm
from openerp.tools.translate import _

from openerp.addons.delivery_carrier_label_postlogistics_shop_logo.postlogistics import (
    web_service
)


class PostlogisticsWebServiceQoQa(web_service.PostlogisticsWebServiceShop):

    def _prepare_recipient(self, picking):
        """ Create a ns0:Recipient as a dict from a partner

        Add a check to ensure we don't write parent name
        of QoQa customer containing email adresse

        :param partner: partner browse record
        :return a dict containing data for ns0:Recipient

        """
        recipient = super(PostlogisticsWebServiceQoQa, self
                          )._prepare_recipient(picking)

        parent = picking.partner_id.parent_id
        # We consider an addresse's parent being a unwanted 'company' name
        # if qoqa_bind_ids is not empty
        if parent.qoqa_bind_ids:
            del recipient['Name2']
            recipient['PersonallyAddressed'] = True

        return recipient

    def _prepare_attributes(self, picking):
        """ Set the Free Text on label for SAV

        On merchandise return we need the RMA number on it

        """
        attributes = super(PostlogisticsWebServiceQoQa, self
                          )._prepare_attributes(picking)

        if picking.claim_id:
            attributes['FreeText'] = picking.claim_id.number
        return attributes

    def _prepare_customer(self, picking):
        """ Create a ns0:Customer as a dict from picking

        Change Postlogistic Customer, thus the sender by 
        your customer's address for RMA claim

        :param picking: picking browse record
        :return a dict containing data for ns0:Customer

        """
        customer = super(PostlogisticsWebServiceQoQa, self
                          )._prepare_customer(picking)

        if picking.claim_id:
            partner = picking.claim_id.partner_id
            if not partner:
                raise orm.except_orm(
                    _('Error'),
                    _('Cannot write sender on label, no partner assigned '
                    'on Claim'))
            sender = {
                'Name1': partner.name,
                'Street': partner.street,
                'ZIP': partner.zip,
                'City': partner.city,
                'Country': partner.country_id.code,
            }
            customer.update(sender)
        return customer
