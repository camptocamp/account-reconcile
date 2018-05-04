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
            ctx = (context and context.copy() or {})
            ctx.update({
                'active_model': 'stock.batch.picking',
                'active_ids': docids,
            })

            label_generate_wiz = self.pool.get(
                'delivery.carrier.label.generate'
            )
            label_generate_id = label_generate_wiz.create(
                cr, uid, {}, ctx)
            label_generate = label_generate_wiz.browse(
                cr, uid, label_generate_id, ctx
            )
            label_generate.action_generate_labels()

            att_obj = self.pool.get('ir.attachment')
            attachment_ids = att_obj.search(
                cr, uid, [('res_id', 'in', docids),
                          ('res_model', '=', 'stock.batch.picking')],
                context=context
            )
            attachments = att_obj.browse(cr, uid, attachment_ids, context)
            return self.process_report(attachments)
        else:
            return super(Report, self).get_pdf(
                cr, uid, docids, report_name,
                html=html, data=data, context=context
            )

    @api.v8  # noqa
    def get_pdf(self, docids, report_name, html=None, data=None):
        if report_name == 'specific_reports.report_batch_picking_labels':
            self.env[
                'delivery.carrier.label.generate'
            ].with_context(
                active_model='stock.batch.picking',
                active_ids=docids
            ).create(
                {}
            ).action_generate_labels()

            attachments = self.env['ir.attachment'].search(
                [('res_id', 'in', docids),
                 ('res_model', '=', 'stock.batch.picking')]
            )
            return self.process_report(attachments)
        else:
            return super(Report, self).get_pdf(docids, report_name, html, data)

    def process_report(self, attachments):
        pdfs = [att.datas.decode('base64') for att in attachments]

        # Add `None` in between each attachment
        # to have a blank page between each carrier label set
        pdf_to_print = [None] * (len(pdfs) * 2 - 1)
        pdf_to_print[0::2] = pdfs

        return self.merge_pdf_in_memory(pdf_to_print)

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
