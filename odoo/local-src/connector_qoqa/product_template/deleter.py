# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from ..unit.deleter import QoQaDeleteSynchronizer

from ..backend import qoqa


@qoqa
class ProductTemplateExportDeleter(QoQaDeleteSynchronizer):
    _model_name = ['qoqa.product.template']
