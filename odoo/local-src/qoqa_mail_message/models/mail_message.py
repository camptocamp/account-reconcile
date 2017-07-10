# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA (Nicolas Bessi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from urlparse import urljoin
from openerp import models, api, _


class QoQaMessage(models.Model):

    _inherit = 'mail.message'

    @api.model
    def _get_qoqa_redirect_url(self, res_id, model):
        """Return an URL that uses the mail/view controller
        to open a given ressource

        :param res_id: the id of a target ressource
        :param model: the model of the target ressource
        :return: an url that point on a given record
        :return type: string
        """
        if not (res_id and model):
            raise ValueError('Model and record id must be supplied')
        if isinstance(res_id, basestring):
            if not res_id.isdigit():
                raise ValueError('The given res_id is not an int')
        try:
            self.env[model]
        except:
            raise ValueError('Model {} is not known'.format(model))
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        action = "/mail/view?model={}&res_id={}".format(
            model,
            res_id
        )
        return urljoin(base_url, action)

    @api.model
    def _extend_body_with_url(self, body, url):
        """Extends mail.message body field with a given url.
        In order to add a link to that url in the message body.

        :param body: a message HTML body
        :param url: the url to add to the message body

        :return: The current body extended with the url
        :return type: string
        """
        body += _(u'<br/><a href="{}">View in Odoo</a>').format(url)
        return body

    @api.model
    def create(self, values):
        """Override create to add "View in Odoo link
        in mail.message body.

        The link is added only if all followers on thread
        only if all follower are internal users
        """
        res_id = values.get('res_id')
        model = values.get('model')
        body = values.get('body')
        if model and res_id and body:
            origin = self.env[model].browse(res_id)
            origin_can_be_tested = hasattr(origin,
                                           'all_followers_are_users')
            if origin_can_be_tested and origin.all_followers_are_users():
                url = self._get_qoqa_redirect_url(res_id, model)
                values['body'] = self._extend_body_with_url(body, url)
        return super(QoQaMessage, self).create(values)
