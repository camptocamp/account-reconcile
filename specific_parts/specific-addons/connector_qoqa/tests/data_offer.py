# -*- coding: utf-8 -*-

"""
Responses returned by the QoQa Web-Services
"""

qoqa_offer = {
    'http://admin.test02.qoqa.com/api/v1/deal/99999999':
u'''{
  "data": {
    "id": 99999999,
    "shop_id": 100,
    "language_id": null,
    "slots_available": 0,
    "is_queue_enabled": 0,
    "shipper_service_id": 2,
    "shipper_rate_id": 1,
    "currency_id": 1,
    "lot_per_package": 1,
    "start_at": "2013-10-14T12:00:00+0200",
    "stop_at": "2013-10-16T12:00:00+0200",
    "notes": "<p>Sav Schumf -Astavel<\/p>",
    "is_active": 1,
    "logistic_status_id": 1,
    "created_at": "2013-10-11T11:55:52+0200",
    "updated_at": "2013-10-11T12:00:30+0200",
    "translations": [
      {
        "id": 8443,
        "deal_id": 5469,
        "language_id": 1,
        "title": "title",
        "content": "<p>content</p>",
        "post_id": 217
      },
      {
        "id": 8444,
        "deal_id": 5469,
        "language_id": 2,
        "title": null,
        "content": null,
        "post_id": 218
      }
    ]
  },
  "user": {
    "errors": null
  },
  "shop": null,
  "uid": null,
  "user_id": 4545,
  "locale": "fr",
  "model": "qoqacore\\\\models\\\\Deal",
  "languages": [
    "fr",
    "de"
  ],
  "language": "qoqacore\\\\models\\\\Language",
  "langs": [
    "fr",
    "de"
  ]
}''',
}
