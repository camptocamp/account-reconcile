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
    "email": "christos.k@bluewin.ch-test",
    "initial_email": null,
    "password": {
      
    },
    "salt": {
      
    },
    "token_reset_pwd": null,
    "ipaddresse": null,
    "time_expire_reset_pwd": null,
    "last_login": "2013-11-19T10:39:52+0100",
    "is_active": 1,
    "firstname": "Christos",
    "lastname": "Kornaros",
    "order_count": 1,
    "bounce_count": null,
    "bounce_date": null,
    "bounce_reason": null,
    "created_at": "2008-06-02T17:40:17+0200",
    "updated_at": "2013-11-19T10:39:52+0100",
    "customer": {
      "id": 16764,
      "user_id": 16764,
      "status_id": 2,
      "media_id": 36933,
      "language_id": 1,
      "origin_shop_id": 2,
      "origin_blog_id": null,
      "amount": 0,
      "referer_user_id": null,
      "created_at": "2011-08-23T00:00:42+0200",
      "updated_at": "2013-04-08T20:37:45+0200"
    },
    "cards": [
      {
        "id": 16202,
        "payment_method_id": 2,
        "payment_provider_id": 7,
        "user_id": 99999999,
        "shop_id": 2,
        "name_on_card": "CHRISTOS KORNAROS",
        "alias_cc": "11703522324597433",
        "masked_cc": "513659xxxxxx1769",
        "exp": "2014-04-01T00:00:00+0200",
        "is_active": 0,
        "created_at": "2012-07-05T15:27:24+0200",
        "updated_at": "2013-04-08T20:32:41+0200"
      },
      {
        "id": 29899,
        "payment_method_id": 2,
        "payment_provider_id": 7,
        "user_id": 99999999,
        "shop_id": 2,
        "name_on_card": "CHRISTOS KORNAROS",
        "alias_cc": "117035223xxxxxxxx",
        "masked_cc": "513659xxxxxx1769",
        "exp": "2014-04-01T00:00:00+0200",
        "is_active": 1,
        "created_at": "2013-04-16T13:56:05+0200",
        "updated_at": "2013-04-16T13:56:05+0200"
      }
    ],
    "addresses": [
      {
        "id": 999999991,
        "user_id": 99999999,
        "firstname": "Christos",
        "lastname": "Kornaros",
        "company": "",
        "street": "Ch. du Rocher 5a",
        "street2": "",
        "code": "1260",
        "city": "Nyon",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 1,
        "created_at": "2013-06-14T09:52:25+0200",
        "updated_at": "2013-06-14T09:52:25+0200"
      },
      {
        "id": 999999992,
        "user_id": 99999999,
        "firstname": "Christos",
        "lastname": "Kornaros",
        "company": "",
        "street": "Ch. En la fin 20",
        "street2": "",
        "code": "1275",
        "city": "Ch\u00e9serex",
        "state": null,
        "country_id": 2,
        "phone": null,
        "mobile": "0793053044",
        "fax": null,
        "digicode": "",
        "is_active": 1,
        "created_at": "2013-04-23T12:01:03+0200",
        "updated_at": "2013-04-23T12:01:03+0200"
      },
      {
        "id": 999999993,
        "user_id": 99999999,
        "firstname": "Christos",
        "lastname": "Kornaros",
        "company": "",
        "street": "Ch. En la fin 20",
        "street2": "",
        "code": "1275",
        "city": "Ch\u00e9serex",
        "state": null,
        "country_id": 1,
        "phone": "0793053044",
        "mobile": "",
        "fax": "",
        "digicode": null,
        "is_active": 1,
        "created_at": "2013-04-16T13:54:57+0200",
        "updated_at": "2013-04-16T13:54:57+0200"
      },
      {
        "id": 999999994,
        "user_id": 99999999,
        "firstname": "Christos",
        "lastname": "Kornaros",
        "company": null,
        "street": "Case postale 44",
        "street2": null,
        "code": "1276",
        "city": "Gingins",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 0,
        "created_at": "2010-06-14T09:07:18+0200",
        "updated_at": "2011-08-27T00:13:26+0200"
      },
      {
        "id": 999999995,
        "user_id": 99999999,
        "firstname": "Christos",
        "lastname": "Kornaros",
        "company": null,
        "street": "Ch. En la fin 20",
        "street2": null,
        "code": "1275",
        "city": "Ch\u00e9serex",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 1,
        "created_at": "2008-06-02T17:41:47+0200",
        "updated_at": "2011-08-26T23:50:33+0200"
      }
    ],
    "comments": [
      {
        "id": 201299,
        "user_id": 99999999,
        "body": "Moi je dis : \"Sant\u00e9 \u00e0 Mr QoQa et aux trois vainqueurs\" ;)",
        "is_active": 1,
        "dislike_count": 0,
        "like_count": 3,
        "created_at": "2013-04-08T20:34:27+0200",
        "updated_at": "2013-04-08T20:34:27+0200"
      },
      {
        "id": 206644,
        "user_id": 99999999,
        "body": "Salut les fans de de bonbons ! Bonne nouvelle le probl\u00e8me de la page 500 lors de la commande est r\u00e9gl\u00e9 :)\r\nR\u00e9galez-vous !!!",
        "is_active": 1,
        "dislike_count": 2,
        "like_count": 10,
        "created_at": "2013-05-08T14:29:14+0200",
        "updated_at": "2013-05-08T15:00:20+0200"
      },
      {
        "id": 210450,
        "user_id": 99999999,
        "body": "@sam5166 et @niarfon Merci pour l'info ! Je vais investiguer ce probl\u00e8me d'erreur 500 afin de vous permettre de commander tranquillement cette bonne Grappa ;) Je vais probablement vous contacter directement car j'ai besoin de plus d'infos.",
        "is_active": 1,
        "dislike_count": 0,
        "like_count": 0,
        "created_at": "2013-05-23T11:14:45+0200",
        "updated_at": "2013-05-23T11:14:45+0200"
      }
    ],
    "votes": [
      {
        "id": 293690,
        "user_id": 99999999,
        "comment_id": 198154,
        "type_id": 2
      },
      {
        "id": 293691,
        "user_id": 99999999,
        "comment_id": 198155,
        "type_id": 2
      },
      {
        "id": 307375,
        "user_id": 99999999,
        "comment_id": 201030,
        "type_id": 1
      },
      {
        "id": 307378,
        "user_id": 99999999,
        "comment_id": 201040,
        "type_id": 1
      },
      {
        "id": 308142,
        "user_id": 99999999,
        "comment_id": 201402,
        "type_id": 1
      },
      {
        "id": 309872,
        "user_id": 99999999,
        "comment_id": 201022,
        "type_id": 2
      },
      {
        "id": 328118,
        "user_id": 99999999,
        "comment_id": 203599,
        "type_id": 1
      },
      {
        "id": 328119,
        "user_id": 99999999,
        "comment_id": 203598,
        "type_id": 1
      },
      {
        "id": 328121,
        "user_id": 99999999,
        "comment_id": 203594,
        "type_id": 1
      },
      {
        "id": 328125,
        "user_id": 99999999,
        "comment_id": 203590,
        "type_id": 1
      },
      {
        "id": 339708,
        "user_id": 99999999,
        "comment_id": 205163,
        "type_id": 1
      },
      {
        "id": 339710,
        "user_id": 99999999,
        "comment_id": 205274,
        "type_id": 1
      },
      {
        "id": 339711,
        "user_id": 99999999,
        "comment_id": 205577,
        "type_id": 1
      },
      {
        "id": 339713,
        "user_id": 99999999,
        "comment_id": 205603,
        "type_id": 1
      },
      {
        "id": 344388,
        "user_id": 99999999,
        "comment_id": 205963,
        "type_id": 1
      },
      {
        "id": 344389,
        "user_id": 99999999,
        "comment_id": 205967,
        "type_id": 1
      },
      {
        "id": 344392,
        "user_id": 99999999,
        "comment_id": 206016,
        "type_id": 1
      },
      {
        "id": 347378,
        "user_id": 99999999,
        "comment_id": 206644,
        "type_id": 1
      },
      {
        "id": 347379,
        "user_id": 99999999,
        "comment_id": 206641,
        "type_id": 1
      },
      {
        "id": 353398,
        "user_id": 99999999,
        "comment_id": 208432,
        "type_id": 1
      },
      {
        "id": 381293,
        "user_id": 99999999,
        "comment_id": 217189,
        "type_id": 1
      },
      {
        "id": 394356,
        "user_id": 99999999,
        "comment_id": 221859,
        "type_id": 1
      },
      {
        "id": 400626,
        "user_id": 99999999,
        "comment_id": 223541,
        "type_id": 1
      }
    ],
    "newsletters": [
      {
        "id": 1,
        "shop_id": 2,
        "name": "qoqa.ch",
        "type_id": 1,
        "created_at": "2011-08-22T23:56:36+0200",
        "updated_at": "2012-10-11T23:33:01+0200"
      },
      {
        "id": 2,
        "shop_id": 3,
        "name": "qoqa.fr",
        "type_id": 1,
        "created_at": "2011-08-22T23:56:36+0200",
        "updated_at": "2012-09-14T12:33:55+0200"
      },
      {
        "id": 3,
        "shop_id": 4,
        "name": "qwine.ch",
        "type_id": 1,
        "created_at": "2011-08-22T23:56:36+0200",
        "updated_at": "2012-10-08T10:46:40+0200"
      },
      {
        "id": 5,
        "shop_id": 7,
        "name": "qsport.ch",
        "type_id": 1,
        "created_at": "2012-02-20T16:09:15+0100",
        "updated_at": "2012-02-20T16:11:11+0100"
      },
      {
        "id": 6,
        "shop_id": 8,
        "name": "qwine.fr",
        "type_id": 1,
        "created_at": "2012-09-10T16:56:37+0200",
        "updated_at": "2012-09-14T12:33:39+0200"
      },
      {
        "id": 7,
        "shop_id": 9,
        "name": "Qstyle.ch",
        "type_id": 2,
        "created_at": "2013-04-15T15:44:50+0200",
        "updated_at": "2013-04-15T15:44:50+0200"
      },
      {
        "id": 8,
        "shop_id": 10,
        "name": "qooking.ch",
        "type_id": 1,
        "created_at": "2013-08-26T15:37:05+0200",
        "updated_at": null
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


qoqa_address = {
    'http://admin.test02.qoqa.com/api/v1/address/999999991':
r'''{
  "data": {
    "id": 999999991,
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
    "email": "guewen@gmail.com-test",
    "initial_email": null,
    "password": {
      
    },
    "salt": {
      
    },
    "token_reset_pwd": null,
    "ipaddresse": null,
    "time_expire_reset_pwd": null,
    "last_login": "2013-11-18T20:24:10+0100",
    "is_active": 1,
    "firstname": "Guewen",
    "lastname": "Baconnier",
    "order_count": 1,
    "bounce_count": null,
    "bounce_date": null,
    "bounce_reason": null,
    "created_at": "2006-12-15T14:53:38+0100",
    "updated_at": "2013-11-18T20:24:10+0100",
    "customer": {
      "id": 4545,
      "user_id": 4545,
      "status_id": 2,
      "media_id": null,
      "language_id": 1,
      "origin_shop_id": 2,
      "origin_blog_id": null,
      "amount": 0,
      "referer_user_id": null,
      "created_at": "2011-08-23T00:00:42+0200",
      "updated_at": "2011-08-23T00:00:42+0200"
    },
    "cards": [
      
    ],
    "addresses": [
      {
        "id": 999999991,
        "user_id": 99999999,
        "firstname": "Guewen",
        "lastname": "Baconnier",
        "company": "",
        "street": "Grand Rue 3",
        "street2": "",
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
      {
        "id": 999999992,
        "user_id": 99999999,
        "firstname": "Guewen",
        "lastname": "Baconnier",
        "company": "",
        "street": "Ruelle du Temple 10",
        "street2": "",
        "code": "1350",
        "city": "Orbe",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 0,
        "created_at": "2009-02-27T09:37:14+0100",
        "updated_at": "2013-08-16T14:27:41+0200"
      },
      {
        "id": 999999993,
        "user_id": 99999999,
        "firstname": "Guewen",
        "lastname": "Baconnier",
        "company": null,
        "street": "Ruelle du Temple 10",
        "street2": null,
        "code": "1350",
        "city": "Orbe",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 0,
        "created_at": "2009-02-27T09:37:14+0100",
        "updated_at": "2011-08-26T23:58:28+0200"
      },
      {
        "id": 999999994,
        "user_id": 99999999,
        "firstname": "Guewen",
        "lastname": "Baconnier",
        "company": null,
        "street": "Ch. de l'Etraz 1",
        "street2": null,
        "code": "1350",
        "city": "Orbe",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 0,
        "created_at": "2007-02-01T00:00:00+0100",
        "updated_at": "2011-08-26T23:44:53+0200"
      },
      {
        "id": 999999995,
        "user_id": 99999999,
        "firstname": "Guewen",
        "lastname": "Baconnier",
        "company": null,
        "street": "Grand-Pont 1",
        "street2": null,
        "code": "1350",
        "city": "Orbe",
        "state": null,
        "country_id": 1,
        "phone": null,
        "mobile": null,
        "fax": null,
        "digicode": null,
        "is_active": 0,
        "created_at": "2007-01-09T00:00:00+0100",
        "updated_at": "2011-08-26T23:44:38+0200"
      }
    ],
    "comments": [
      
    ],
    "votes": [
      
    ],
    "newsletters": [
      {
        "id": 1,
        "shop_id": 2,
        "name": "qoqa.ch",
        "type_id": 1,
        "created_at": "2011-08-22T23:56:36+0200",
        "updated_at": "2012-10-11T23:33:01+0200"
      },
      {
        "id": 3,
        "shop_id": 4,
        "name": "qwine.ch",
        "type_id": 1,
        "created_at": "2011-08-22T23:56:36+0200",
        "updated_at": "2012-10-08T10:46:40+0200"
      },
      {
        "id": 8,
        "shop_id": 10,
        "name": "qooking.ch",
        "type_id": 1,
        "created_at": "2013-08-26T15:37:05+0200",
        "updated_at": null
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
