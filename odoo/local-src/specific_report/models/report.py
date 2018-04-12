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

    @api.v7
    def get_pdf(self, cr, uid, docids, report_name, html=None, data=None,
                context=None):
        if report_name == 'specific_reports.report_batch_picking_labels':
            batches = self.pool.get('stock.batch.picking').browse(
                cr, uid, docids
            )
            if context is None:
                context = {}
            context.update({
                'active_model': 'stock.batch.picking',
                'active_ids': docids,
            })
            label_generate_id = self.pool.get(
                'delivery.carrier.label.generate'
            ).create(cr, uid, {}, context=context)
            label_generate = self.pool.get(
                'delivery.carrier.label.generate'
            ).browse(
                cr, uid, label_generate_id, context
            )
            return self.process_report(batches, label_generate)
        else:
            return super(Report, self).get_pdf(
                cr, uid, docids, report_name,
                html=html, data=data, context=context
            )

    @api.v8  # noqa
    def get_pdf(self, docids, report_name, html=None, data=None):
        if report_name == 'specific_reports.report_batch_picking_labels':
            batches = self.env['stock.batch.picking'].browse(docids)
            label_generate = self.env[
                'delivery.carrier.label.generate'
            ].with_context(
                active_model='stock.batch.picking', active_ids=docids
            ).create({})
            return self.process_report(batches, label_generate)
        else:
            return super(Report, self).get_pdf(docids, report_name, html, data)

    def process_report(self, batches, label_generate):
        pdf_to_print = []
        for batch in batches:
            labels = label_generate._get_all_pdf(batch)
            # `+ [None]` The goal is to add a blank page between each
            # set of carrier labels
            pdf_to_print += [label.decode('base64') for label in labels if
                             label] + [None]
        # the last None was removed to avoid having a blank page at the end
        # of the document
        return self.merge_pdf_in_memory(pdf_to_print[:-1])

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
