# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
from cStringIO import StringIO

import requests

from PIL import Image

from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.queue.job import job

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa
from ..connector import get_environment


@qoqa
class QoQaProductImageImporter(ConnectorUnit):
    _model_name = 'qoqa.product.template'

    def read_image(self, url):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image = response.content
        try:
            # just check if we really have an image
            Image.open(StringIO(image))
        except IOError:
            # not an image
            return
        return base64.b64encode(image)

    def run(self, qoqa_id):
        binder = self.binder_for()
        binding = binder.to_openerp(qoqa_id)
        if not binding.exists():
            return  # ignore, record deleted in Odoo

        adapter = self.unit_for(QoQaAdapter)
        values = adapter.read(qoqa_id)

        # get template image
        template_url = values['data']['attributes'].get('image_file_url')
        if template_url:
            template_image = self.read_image(template_url)
            if template_image:
                binding.image = template_image

        # get variant images
        variant_binder = self.binder_for('qoqa.product.product')
        for variant_values in values['included']:
            variant_id = variant_values['id']
            variant_binding = variant_binder.to_openerp(variant_id)
            if not variant_binding:
                continue

            variant_url = variant_values['attributes'].get('big_picture_url')
            if not variant_url:
                continue

            variant_image = self.read_image(variant_url)
            if variant_image:
                variant_binding.image = variant_image


@job(default_channel='root.connector_qoqa.normal')
def import_product_images(session, model_name, backend_id, qoqa_id):
    with get_environment(session, model_name, backend_id) as connector_env:
        importer = connector_env.get_connector_unit(QoQaProductImageImporter)
        importer.run(qoqa_id)
