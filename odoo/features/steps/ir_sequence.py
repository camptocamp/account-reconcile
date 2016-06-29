# -*- coding: utf-8 -*-
import logging

from support import *
from support.tools import model

logger = logging.getLogger('openerp.behave')


@given('I copy the sequence next number from "{source_sequence_code}" to "{target_sequence_code}"')
def impl(ctx, source_sequence_code, target_sequence_code):
    Sequence = model('ir.sequence')
    source_sequence = Sequence.get([('code', '=', source_sequence_code)])
    target_sequence = Sequence.get([('code', '=', target_sequence_code)])
    target_sequence.write(
        {'number_next': source_sequence.number_next}
    )
