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

from openerp.addons.connector.backend import Backend

qoqa = Backend('qoqa')
""" Generic QoQa Backend. """


# qoqa.ch and qoqa.fr
qoqa_all = Backend(parent=qoqa)
""" QoQa Backend common to qoqa.ch and qoqa.fr

Can't be used directly but can be used to share the knowledge
for both websites."""

qoqa_ch = Backend(parent=qoqa_all, version='qoqa.ch')
""" QoQa Backend for qoqa.ch """

qoqa_fr = Backend(parent=qoqa_all, version='qoqa.fr')
""" QoQa Backend for qoqa.fr """


# qwine.ch and qwine.fr
qwine_all = Backend(parent=qoqa)
""" QoQa Backend common to qwine.ch and qwine.fr

Can't be used directly but can be used to share the knowledge
for both websites."""

qoqa_fr = Backend(parent=qwine_all, version='qwine.ch')
""" QoQa Backend for qwine.ch """

qwine_fr = Backend(parent=qwine_all, version='qwine.fr')
""" QoQa Backend for qwine.fr """


# qsport.ch
qsport_ch = Backend(parent=qoqa, version='qsport.ch')
""" QoQa Backend for qsport.ch """


# qooking.ch
qooking_ch = Backend(parent=qoqa, version='qooking.ch')
""" QoQa Backend for qooking.ch """
