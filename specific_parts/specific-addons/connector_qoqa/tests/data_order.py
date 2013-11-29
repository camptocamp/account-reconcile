# -*- coding: utf-8 -*-

"""
Responses returned by the QoQa Web-Services
"""

qoqa_order = {
    'http://admin.test02.qoqa.com/api/v1/order/99999999':
r'''{
  "data": {
    "id": 99999999,
    "shop_id": 100,
    "deal_id": 99999999,
    "user_id": 99999999,
    "billing_address_id": 999999991,
    "shipping_address_id": 999999991,
    "shipper_relay_id": null,
    "type_id": 2,
    "status_id": 3,
    "shipper_service_id": 2,
    "application_origin_id": null,
    "created_at": "2013-10-11T17:34:41+0200",
    "updated_at": "2013-10-11T17:35:03+0200",
    "order_items": [
      {
        "id": 99999999,
        "order_id": 99999999,
        "item_id": 99999999,
        "type_id": 1,
        "status_id": 1,
        "quantity": 2,
        "delivery_at": "2013-10-28T00:00:00+0100",
        "created_at": "2013-10-11T17:34:42+0200",
        "updated_at": "2013-10-11T17:34:42+0200"
      }
    ],
    "items": [
      {
        "id": 99999999,
        "type_id": 1,
        "offer_id": 99999999,
        "variation_id": 99999999,
        "promo_id": 99999999,
        "stock_id": null,
        "lot_size": 6,
        "custom_text": "custom text",
        "created_at": "2013-10-11T17:34:42+0200",
        "updated_at": "2013-10-11T17:34:42+0200"
      }
    ],
    "payments": [
      {
        "id": 1377427,
        "parent_id": null,
        "type_id": 2,
        "user_id": 34238,
        "order_id": 1010695,
        "invoice_id": 898901,
        "currency_id": 1,
        "status_id": 5,
        "settlement_status_id": 2,
        "method_id": 1,
        "provider_id": 7,
        "voucher_id": null,
        "account": "3000007003",
        "amount": 2950,
        "transaction": "131011173501376765",
        "trx_date": "2013-10-11T17:35:03+0200",
        "acq_auth_code": 761035,
        "batch": null,
        "book_line_id": null,
        "payout_id": null,
        "created_at": "2013-10-11T17:34:59+0200",
        "updated_at": "2013-10-11T17:35:03+0200"
      }
    ],
    "order_returns": [
      
    ],
    "invoices": [
      {
        "id": 898901,
        "shop_id": 100,
        "user_id": 34238,
        "address_id": 874724,
        "currency_id": 1,
        "type_id": 1,
        "status_id": 2,
        "reference": "XRIHJQ",
        "vref": null,
        "issued_at": "2013-10-11T00:00:00+0200",
        "total": 2950,
        "footer": null,
        "created_at": "2013-10-11T17:35:03+0200",
        "updated_at": "2013-10-11T17:35:03+0200",
        "item_details": [
          {
            "id": 2118866,
            "invoice_id": 898901,
            "item_id": 99999999,
            "vat_id": 6,
            "type_id": 1,
            "credit_acct": null,
            "debit_acct": null,
            "quantity": 2,
            "unit_price": 10500,
            "ignore_credit": 0,
            "is_net_price": 1,
            "book_line_id": null,
            "created_at": "2013-10-11T17:35:03+0200",
            "updated_at": "2013-10-11T17:35:03+0200",
            "item": {
              "id": 3568541,
              "type_id": 1,
              "offer_id": 99999999,
              "variation_id": 99999999,
              "promo_id": 99999999,
              "stock_id": null,
              "lot_size": 6,
              "custom_text": "custom text",
              "created_at": "2013-10-11T17:34:42+0200",
              "updated_at": "2013-10-11T17:34:42+0200"
            }
          },
          {
            "id": 2118867,
            "invoice_id": 898901,
            "item_id": 999999991,
            "vat_id": 6,
            "type_id": 1,
            "credit_acct": null,
            "debit_acct": null,
            "quantity": 1,
            "unit_price": -950,
            "ignore_credit": 0,
            "is_net_price": 1,
            "book_line_id": null,
            "created_at": "2013-10-11T17:35:03+0200",
            "updated_at": "2013-10-11T17:35:03+0200",
            "item": {
              "id": 3568542,
              "type_id": 3,
              "offer_id": null,
              "variation_id": null,
              "promo_id": 99999999,
              "stock_id": null,
              "lot_size": 1,
              "custom_text": null,
              "created_at": "2013-10-11T17:35:03+0200",
              "updated_at": "2013-10-11T17:35:03+0200"
            }
          },
          {
            "id": 2118868,
            "invoice_id": 898901,
            "item_id": 999999992,
            "vat_id": 6,
            "type_id": 1,
            "credit_acct": null,
            "debit_acct": null,
            "quantity": 1,
            "unit_price": 600,
            "ignore_credit": 0,
            "is_net_price": 1,
            "book_line_id": null,
            "created_at": "2013-10-11T17:35:03+0200",
            "updated_at": "2013-10-11T17:35:03+0200",
            "item": {
              "id": 3568543,
              "type_id": 2,
              "offer_id": null,
              "variation_id": null,
              "promo_id": null,
              "stock_id": null,
              "lot_size": 1,
              "custom_text": null,
              "created_at": "2013-10-11T17:35:03+0200",
              "updated_at": "2013-10-11T17:35:03+0200"
            }
          }
        ]
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
  "model": "qoqacore\\models\\Order",
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
