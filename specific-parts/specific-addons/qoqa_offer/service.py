# -*- coding: utf-8 -*-
"""
Utility script used to generate the XML data for the delivery.service
from the HTML source of the QoQa backend.
"""

from StringIO import StringIO
from lxml import etree
import re
import string


def slugify(text):
    text = text.replace(' ', '_').lower()
    return re.sub(r'\W', '', text)

template = """
        <record model="delivery.service" id="delivery_service_%(slug_name)s">
            <field name="name">%(name)s</field>
        </record>
"""

xml = '<select><option value="">---------</option><option value="1">(manual/undefined)</option><option value="2" selected="selected">PostPac PRI+SI Std</option><option value="3">PostPac PRI+SI MAN</option><option value="4">PostPac PRI+SI SP</option><option value="5">A-Mail B5 0-100g 0-2cm</option><option value="6">A-Mail B5 0-100g 2-5cm</option><option value="7">A-Mail B5 100-250g 0-2cm</option><option value="8">A-Mail B5 100-250g 2-5cm</option><option value="9">Legacy FR</option><option value="10">Wine Transport</option><option value="11">VinoLog</option><option value="12">Manual w/phone</option><option value="13">Standard </option><option value="14">Standard w/phone </option><option value="15">Legacy QWFR</option><option value="16">PostPac PRI</option><option value="17">So Colissimo</option><option value="18">Client appointments</option></select>'

slugs = set()
parser = etree.HTMLParser()
tree = etree.parse(StringIO(xml), parser)
for option in tree.xpath('//select/option'):
    text = option.text.strip()
    slug = slugify(text)
    if slug in slugs:
        raise Exception("slug %s already exists" % slug)
    slugs.add(slug)
    print template % {'name': text,
                      'slug_name': slug}
