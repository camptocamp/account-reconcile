# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.exception import (ConnectorException,
                                                RetryableJobError)


class QoQaError(ConnectorException):
    """ Base Exception class for the QoQa Connector. """


class QoQaAPIError(QoQaError):
    """ Error with the QoQa API. """


class QoQaResponseNotParsable(QoQaAPIError):
    """ Happens when a response from the QoQa API is not parsable. """


class QoQaResponseError(QoQaAPIError):
    """ The API responded but gave details about errors """

    no_reason = u'Unknown error'

    def __init__(self, errors):
        """

        :param errors: errors of the API, list of tuples
                       (code, title, detail)
        """
        self.errors = errors

    def __str__(self):
        if not self.errors:
            return self.no_reason
        else:
            return ','.join([
                u"[code {0}] {1}: {2}".format(code, title, detail)
                for code, title, detail in self.errors
            ])


class QoQaAPIAuthError(QoQaResponseError):
    """ Authentication error with the QoQa API. """

    no_reason = (u'The call could not be completed because it was not '
                 u'authenticated or the authentication rejected it.')


class OrderImportRuleRetry(RetryableJobError):
    """ The sale order import will be retried later. """


class QoQaRecordDoesNotExist(QoQaResponseError):
    """ The QoQa API returns that a record does not exists """

    no_reason = u'Record does not exist on the QoQa side.'
