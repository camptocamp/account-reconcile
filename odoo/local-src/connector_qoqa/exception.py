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

from openerp.addons.connector.exception import (ConnectorException,
                                                RetryableJobError)


class QoQaError(ConnectorException):
    """ Base Exception class for the QoQa Connector. """


class QoQaAPIError(QoQaError):
    """ Error with the QoQa API. """


class QoQaAPIAuthError(QoQaAPIError):
    """ Authentication error with the QoQa API. """


class QoQaResponseNotParsable(QoQaAPIError):
    """ Happens when a response from the QoQa API is not parsable. """


class QoQaResponseError(QoQaAPIError):
    """ The API responded but gave details about errors """

    def __init__(self, errors):
        """

        :param errors: errors of the API, list of tuples
                       (type, code, message)
        """
        self.errors = errors

    def __str__(self):
        if not self.errors:
            return 'Unknow error'
        else:
            return ','.join([
                "[{0} {1}]: {2}".format(errtype, code, msg)
                for errtype, code, msg in self.errors
            ])


class OrderImportRuleRetry(RetryableJobError):
    """ The sale order import will be retried later. """
