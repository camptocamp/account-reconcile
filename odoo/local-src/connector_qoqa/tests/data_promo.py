# -*- coding: utf-8 -*-

# flake8: noqa

"""
Responses returned by the QoQa Web-Services
"""

qoqa_promo = {
    'http://admin.test02.qoqa.com/api/v1/promo/99999999':
r'''{
  "data": {
    "id": 99999999,
    "company_id": 42,
    "promo_type_id": 4,
    "currency_id": 1,
    "amount": 950,
    "start_at": "2013-10-13T12:00:00+0200",
    "stop_at": "2014-01-13T12:01:43+0100",
    "description": "staff",
    "created_at": "2013-10-13T12:32:43+0200",
    "updated_at": "2013-10-13T12:32:43+0200",
    "user_policy_id": 2,
    "shipping_policy_id": 8,
    "translations": [
      {
        "id": 1403,
        "promo_id": 17424,
        "language_id": 1,
        "name": "palmer"
      },
      {
        "id": 1404,
        "promo_id": 17424,
        "language_id": 2,
        "name": "palmer"
      }
    ],
    "codes": [
      {
        "id": 470434,
        "promo_id": 17424,
        "voucher_id": null,
        "name": "HPM3NNJB9G",
        "is_active": 1
      }
    ],
    "items": [
      {
        "id": 3571497,
        "type_id": 1,
        "offer_id": 5407,
        "variation_id": 10071,
        "promo_id": 17424,
        "stock_id": null,
        "lot_size": 1,
        "custom_text": null,
        "created_at": "2013-10-13T12:33:30+0200",
        "updated_at": "2013-10-13T12:33:30+0200"
      },
      {
        "id": 3571502,
        "type_id": 3,
        "offer_id": null,
        "variation_id": null,
        "promo_id": 17424,
        "stock_id": null,
        "lot_size": 1,
        "custom_text": null,
        "created_at": "2013-10-13T12:34:50+0200",
        "updated_at": "2013-10-13T12:34:50+0200"
      }
    ],
    "user_promos": [
      {
        "id": 6134,
        "user_id": 204841,
        "promo_id": 17424,
        "code_id": 470434,
        "remaining_amount": 0,
        "created_at": "2013-10-13T12:32:43+0200",
        "updated_at": "2013-10-13T12:34:50+0200"
      }
    ],
    "promo_shops": [
      {
        "id": 497,
        "promo_id": 17424,
        "shop_id": 4,
        "created_at": "2013-10-13T12:32:43+0200",
        "updated_at": "2013-10-13T12:32:43+0200"
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
  "model": "qoqacore\\models\\Promo",
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
