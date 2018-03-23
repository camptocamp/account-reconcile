# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api

import logging
import StringIO
import pyPdf


_logger = logging.getLogger(__name__)


class Report(models.Model):
    _inherit = 'report'

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        if report_name == 'specific_reports.report_batch_picking_labels':
            batches = self.env['stock.batch.picking'].browse(docids)
            dclg = self.env['delivery.carrier.label.generate'].with_context(
                active_model='stock.batch.picking', active_ids=docids
            ).create({})
            pdf_to_print = []
            for batch in batches:
                labels = dclg._get_all_pdf(batch)
                pdf_to_print += [label.decode('base64')
                                 for label in labels if label] + [None]
            return self.merge_pdf_in_memory(pdf_to_print[:-1])
        else:
            return super(Report, self).get_pdf(docids, report_name, html, data)

    def merge_pdf_in_memory(self, docs):
        streams = []
        writer = pyPdf.PdfFileWriter()
        for doc in docs:
            if doc:
                current_buff = StringIO.StringIO()
                streams.append(current_buff)
                current_buff.write(doc)
                current_buff.seek(0)
                reader = pyPdf.PdfFileReader(current_buff)
                for page in xrange(reader.getNumPages()):
                    writer.addPage(reader.getPage(page))
            else:
                writer.addBlankPage()
        buff = StringIO.StringIO()
        try:
            # The writer close the reader file here
            writer.write(buff)
            return buff.getvalue()
        except IOError:
            raise
        finally:
            buff.close()
            for stream in streams:
                stream.close()
