# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

import requests
from requests_oauthlib import OAuth1Session
from openerp.osv import orm, fields

REQUEST_URL_PART = "/oauth1.0a/request_token"
ACCESS_URL_PART = "/oauth1.0a/access_token"


class qoqa_backend_oauth(orm.TransientModel):
    """
    Wizard to get the OAuth token access.
    """
    _name = 'qoqa.backend.oauth'
    _description = 'QoQa Backend OAuth Wizard'
    _columns = {
        'backend_id': fields.many2one('qoqa.backend',
                                      'QoQa Backend',
                                      required=True),
        'client_key': fields.related(
            'backend_id', 'client_key',
            type='char',
            string='Client Key'),
        'client_secret': fields.related(
            'backend_id', 'client_secret',
            type='char',
            string='Client Secret'),
        'pin': fields.char('PIN'),  # OAuth verifier
        'authorize_url': fields.char('Authorize URL', readonly=True),
        'request_key': fields.char('Request Key', readonly=True),
        'request_secret': fields.char('Request Secret', readonly=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(qoqa_backend_oauth, self).default_get(
            cr, uid, fields, context=context)
        if context.get('active_model') != 'qoqa.backend':
            return res
        backend_id = context.get('active_id')
        if not backend_id:
            return res
        backend_obj = self.pool.get('qoqa.backend')
        backend = backend_obj.browse(cr, uid, backend_id, context=context)
        res.update({
            'backend_id': backend_id,
            'client_key': backend.client_key,
            'client_secret': backend.client_secret,
            'authorize_url': context.get('oauth_auth_url'),
            'request_key': context.get('oauth_request_key'),
            'request_secret': context.get('oauth_request_secret'),
        })
        return res

    def request_token(self, cr, uid, ids, context=None):
        """ Request the authorization tokens from the OAuth API,

        using the client key and client secret.

        First part of the process.
        """
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "Only 1 ID accepted, got %r" % ids
            ids = ids[0]
        form = self.browse(cr, uid, ids, context=context)
        # request the tokens and get the autorization url
        # from the OAuth API
        oauth = OAuth1Session(form.client_key,
                              client_secret=form.client_secret)
        url = form.backend_id.url + REQUEST_URL_PART
        fetch_response = oauth.fetch_request_token(url)
        authorize_url = fetch_response.get('authorize_url')
        request_key = fetch_response.get('oauth_token')
        request_secret = fetch_response.get('oauth_token_secret')
        auth_url = oauth.authorization_url(authorize_url)

        # the wizards reopens itself with tokens and url in the context
        # for the second step: request access tokens
        data_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        action_xmlid = ('connector_qoqa', 'action_qoqa_backend_oauth')
        __, action_id = data_obj.get_object_reference(cr, uid, *action_xmlid)
        action = act_obj.read(cr, uid, [action_id], context=context)[0]
        action['context'] = {'oauth_request_key': request_key,
                             'oauth_request_secret': request_secret,
                             'oauth_auth_url': auth_url,
                             'active_id': form.backend_id.id,
                             'active_ids': [form.backend_id.id],
                             'active_model': 'qoqa.backend',
                             }
        return action

    def access_token(self, cr, uid, ids, context=None):
        """ Request the access tokens from the OAuth API

        Second part of the process.
        """
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "Only 1 ID accepted, got %r" % ids
            ids = ids[0]
        form = self.browse(cr, uid, ids, context=context)
        oauth = OAuth1Session(form.client_key,
                              client_secret=form.client_secret,
                              resource_owner_key=form.request_key,
                              resource_owner_secret=form.request_secret,
                              verifier=form.pin)
        url = form.backend_id.url + ACCESS_URL_PART
        oauth_tokens = oauth.fetch_access_token(url)
        access_token = oauth_tokens.get('oauth_token')
        access_token_secret = oauth_tokens.get('oauth_token_secret')
        form.backend_id.write({
            'access_token': access_token,
            'access_token_secret': access_token_secret,
        })
        return {'type': 'ir.actions.act_window_close'}
