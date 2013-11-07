# -*- coding: utf-8 -*-

"""
Responses returned by the QoQa Web-Services
"""

qoqa_voucher = {
    'http://admin.test02.qoqa.com/api/v1/voucher/99999999':
r'''{
  "data": {
    "id": 99999999,
    "user_id": 99999999,
    "company_id": 42,
    "shop_issuer_id": 100,
    "currency_id": 1,
    "amount": 2000,
    "start_at": "2012-10-31T00:00:00+0100",
    "stop_at": "2013-10-31T00:00:00+0100",
    "description": "Voucher generated with mailing n\u00b09488 \/ retard livraison oreiller Biotex",
    "created_at": "2012-10-31T11:38:17+0100",
    "updated_at": "2013-10-10T18:44:55+0200",
    "remaining_amount": 0
  },
  "user": {
    "errors": null
  },
  "shop": null,
  "uid": null,
  "user_id": 4545,
  "locale": "fr",
  "model": "qoqacore\\models\\Voucher",
  "languages": [
    "fr",
    "de"
  ],
  "language": "qoqacore\\models\\Language",
  "langs": [
    "fr",
    "de"
  ]
}''',
}
