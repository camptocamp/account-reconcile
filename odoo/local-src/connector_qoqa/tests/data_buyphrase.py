# -*- coding: utf-8 -*-

# flake8: noqa

"""
Responses returned by the QoQa Web-Services
"""

qoqa_buyphrase = {
    'http://admin.test02.qoqa.com/api/v1/buyphrase/99999999':
r'''{
  "data": {
    "id": 99999999,
    "shop_id": 100,
    "is_active": 1,
    "created_at": "2012-06-25T11:37:12+0200",
    "updated_at": "2013-04-02T14:58:19+0200",
    "action": 1,
    "translations": [
      {
        "id": 56,
        "buyphrase_id": 38,
        "language_id": 1,
        "buy_text": "Nickel pour le Paleo !",
        "definition": "<p>Oui, c&#39;est ici que vous devez cliquer pour commander le produit du jour ! :)</p>",
        "created_at": "2012-06-25T11:37:12+0200",
        "updated_at": "2013-04-02T14:58:19+0200"
      },
      {
        "id": 57,
        "buyphrase_id": 38,
        "language_id": 2,
        "buy_text": "Jetzt zuschlagen!",
        "definition": "<p>Eigentlich kurz gesagt ist dies der Bestell-Button :-)<\/p>\r\n",
        "created_at": "2012-06-25T11:37:12+0200",
        "updated_at": "2013-04-02T14:58:19+0200"
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
  "model": "qoqacore\\models\\Buyphrase",
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
