# -*- coding: utf-8 -*-

"""
Responses returned by the QoQa Web-Services
"""

qoqa_user = {
    'http://admin.test02.qoqa.com/api/v1/user/':
r'''
{
  "data": [{"id": 99999999},],
  "user": {"errors": null},
  "shop": null,
  "uid": null,
  "user_id": 16764,
  "locale": "fr",
  "model": "qoqacore\\models\\Order",
  "languages": ["fr", "de"],
  "language": "qoqacore\\models\\Language",
  "langs": ["fr", "de"]
}
    ''',
    'http://admin.test02.qoqa.com/api/v1/user/99999999':
r'''{
  "data": {
    "id": 99999999,
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
  "model": "qoqacore\\models\\User",
  "languages": [
    "fr",
    "de"
  ],
  "language": "qoqacore\\models\\Language",
  "langs": [
    "fr",
    "de"
  ]
}'''
}


qoqa_address = {
    'http://admin.test02.qoqa.com/api/v1/address/99999999':
r'''{
  "data": {
    "id": 99999999,
    "user_id": 99999999,
    "firstname": "Guewen",
    "lastname": "Baconnier",
    "company": "",
    "street": "Grand Rue 3",
    "street2": "--",
    "code": "1350",
    "city": "Orbe",
    "state": null,
    "country_id": 1,
    "phone": null,
    "mobile": null,
    "fax": null,
    "digicode": null,
    "is_active": 1,
    "created_at": "2013-06-10T09:54:15+0200",
    "updated_at": "2013-06-10T09:54:15+0200"
  },
  "user": {
    "errors": null
  },
  "shop": null,
  "uid": null,
  "user_id": 4545,
  "locale": "fr",
  "model": "qoqacore\\models\\Address",
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
    'http://admin.test02.qoqa.com/api/v1/user/99999999':
r'''{
  "data": {
    "id": 99999999,
    "suspicious": 0,
    "name": "guewen",
    "email": "guewen@gmail.com",
    "initial_email": null,
    "password": {
      
    },
    "salt": {
      
    },
    "token_reset_pwd": null,
    "ipaddresse": null,
    "time_expire_reset_pwd": null,
    "last_login": "2013-11-04T12:03:30+0100",
    "is_active": 1,
    "firstname": "Guewen",
    "lastname": "Baconnier",
    "order_count": 1,
    "bounce_count": null,
    "bounce_date": null,
    "bounce_reason": null,
    "created_at": "2006-12-15T14:53:38+0100",
    "updated_at": "2013-11-04T12:03:30+0100"
  },
  "user": {
    "errors": null
  },
  "shop": null,
  "uid": null,
  "user_id": 4545,
  "locale": "fr",
  "model": "qoqacore\\models\\User",
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
