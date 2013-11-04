# -*- coding: utf-8 -*-

"""
Responses returned by the QoQa Web-Services
"""

qoqa_user = {
    'http://admin.test02.qoqa.com/api/v1/user/':
u'''
{
  "data": [{"id": 9999999},],
  "user": {"errors": null},
  "shop": null,
  "uid": null,
  "user_id": 16764,
  "locale": "fr",
  "model": "qoqacore\\\\models\\\\Order",
  "languages": ["fr", "de"],
  "language": "qoqacore\\\\models\\\\Language",
  "langs": ["fr", "de"]
}
    ''',
    'http://admin.test02.qoqa.com/api/v1/user/9999999':
u'''{
  "data": {
    "id": 9999999,
    "suspicious": 0,
    "name": "Mykonos",
    "email": "christos.k@bluewin.ch",
    "initial_email": null,
    "password": {
      
    },
    "salt": {
      
    },
    "token_reset_pwd": null,
    "ipaddresse": null,
    "time_expire_reset_pwd": null,
    "last_login": "2013-11-04T13:52:01+0100",
    "is_active": 1,
    "firstname": "Christos",
    "lastname": "Kornaros",
    "order_count": 1,
    "bounce_count": null,
    "bounce_date": null,
    "bounce_reason": null,
    "created_at": "2008-06-02T17:40:17+0200",
    "updated_at": "2013-11-04T13:52:01+0100"
  },
  "user": {
    "errors": null
  },
  "shop": null,
  "uid": null,
  "user_id": 4545,
  "user_token": {
    "errors": null
  },
  "locale": "fr",
  "model": "qoqacore\\\\models\\\\User",
  "languages": [
    "fr",
    "de"
  ],
  "language": "qoqacore\\\\models\\\\Language",
  "langs": [
    "fr",
    "de"
  ]
}'''
}
