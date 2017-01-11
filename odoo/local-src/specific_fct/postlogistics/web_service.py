# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _
from openerp.exceptions import UserError
import re

try:
    from suds.client import Client
    from suds.transport.http import HttpAuthenticated
except ImportError:
    _logger.warning(
        'suds library not found. '
        'If you plan to use it, please install the suds library '
        'from https://pypi.python.org/pypi/suds')

from openerp.addons.delivery_carrier_label_postlogistics_shop_logo\
    .postlogistics import web_service

pickpost_match = re.compile(r'^Pick ?Post ?.*|^My ?Post ?24 ?.*',
                            re.UNICODE | re.IGNORECASE)


class PostlogisticsWebServiceQoQa(web_service.PostlogisticsWebServiceShop):

    def init_connection(self, company):
        t = HttpAuthenticated(
            username=company.postlogistics_username,
            password=company.postlogistics_password,
            timeout=180)
        self.client = Client(
            company.postlogistics_wsdl_url,
            transport=t)

    def _prepare_recipient(self, picking):
        """ Create a ns0:Recipient as a dict from a partner

        Add a check to ensure we don't write parent name
        of QoQa customer containing email adresse

        :param partner: partner browse record
        :return a dict containing data for ns0:Recipient

        """
        recipient = super(PostlogisticsWebServiceQoQa, self
                          )._prepare_recipient(picking)

        partner = picking.partner_id
        parent = partner.parent_id
        # We consider an addresse's parent being a unwanted 'company' name
        # if qoqa_bind_ids is not empty
        if parent.qoqa_bind_ids:
            del recipient['Name2']
            recipient['PersonallyAddressed'] = True
            # Let's forge the address lines as street1 and street2
            # must keep order as company name could be writen in
            # street1
            address_lines = []
            address_lines.append(partner.name)
            address_lines.append(partner.street)
            if partner.street2:
                # 35 is the size limit of an address line in labels
                if len(partner.street2) > 35:
                    street2_1 = partner.street2[:35]
                    street2_2 = partner.street2[35:]
                    address_lines.append(street2_1)
                    address_lines.append(street2_2)
                else:
                    address_lines.append(partner.street2)

            recipient['LabelAddress'] = {
                'LabelLine': address_lines
            }
        # Search for PickPost/MyPost24. If present:
        # - set street as Name2
        # - set street2 as Street
        pickpost = re.search(pickpost_match, partner.street)
        if pickpost:
            recipient['Name2'] = partner.street
            if partner.street2:
                del recipient['AddressSuffix']
                recipient['Street'] = partner.street2
            else:
                del recipient['Street']
        return recipient

    def _prepare_attributes(self, picking):
        """ Set the Free Text on label for SAV

        On merchandise return we need the RMA number on it
        On deliveries, we need the offer ID and the sale ID

        """
        attributes = super(PostlogisticsWebServiceQoQa, self
                           )._prepare_attributes(picking)

        if (picking.picking_type_code == 'outgoing' and
                picking.offer_id and picking.sale_id):
            attributes['FreeText'] = (picking.offer_id.ref +
                                      "." +
                                      picking.sale_id.name)
        elif picking.claim_id:
            attributes['FreeText'] = picking.claim_id.code
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

        if picking.claim_id and picking.picking_type_code == 'incoming':
            partner = picking.claim_id.delivery_address_id
            if not partner:
                raise UserError(
                    _('Cannot write sender on label, no delivery address '
                      'assigned on Claim'))
            sender = {
                # only 25 character per address line for sender
                'Name1': partner.name[:24],
                'Street': partner.street,
                'ZIP': partner.zip,
                'City': partner.city,
                'Country': partner.country_id.code,
            }
            customer.update(sender)
            # remove logo
            if 'Logo' in customer:
                del customer['Logo']
            if 'LogoFormat' in customer:
                del customer['LogoFormat']

        return customer
