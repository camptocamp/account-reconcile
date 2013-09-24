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

import mock
from contextlib import contextmanager
from functools import partial


def get_qoqa_response(responses, url):
    if not url in responses:
        raise Exception('Unhandled request: %s' % url)
    return responses[url]


@contextmanager
def mock_api_responses(responses):
    """
    :param responses: responses returned by QoQa
    :type responses: dict
    """
    with mock.patch('requests.get') as mock_get:
        mock_get.side_effect = partial(get_qoqa_response, responses)
        yield
