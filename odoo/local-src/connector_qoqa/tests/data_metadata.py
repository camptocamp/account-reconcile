# -*- coding: utf-8 -*-

# flake8: noqa

"""
Responses returned by the QoQa Web-Services
"""

qoqa_shops = {
    'http://admin.test02.qoqa.com/api/v1/shops/':
r'''{
  "data": [
    {
      "id": 100,
      "name": "Qtest.ch",
      "company": {
        "id": 42,
        "name": "QoQa Services SA"
      },
      "domain": "ch.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_2_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_2_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 2,
      "name": "QoQa.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "ch.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_2_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_2_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 4,
      "name": "Qwine.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qw.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_4_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_4_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_qwine_ch_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qwine_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 7,
      "name": "Qsport.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qs.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_7_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_7_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_qsport_ch_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qsport_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 9,
      "name": "Qstyle.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qst.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_9_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_9_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        
      ]
    },
    {
      "id": 3,
      "name": "QoQa.fr",
      "company": {
        "id": 2,
        "name": "QoQa Services France SARL"
      },
      "domain": "fr.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_3_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_3_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        }
      ]
    },
    {
      "id": 8,
      "name": "Qwine.fr",
      "company": {
        "id": 2,
        "name": "QoQa Services France SARL"
      },
      "domain": "qwfr.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_8_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_8_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_qwine_ch_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qwine_v1.png"
      },
      "languages": [
        
      ]
    },
    {
      "id": 10,
      "name": "Qooking.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qookingch.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_10_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_10_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        
      ]
    }
  ],
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
  "language": "qoqacore\\\\models\\\\Language",
  "langs": [
    "fr",
    "de"
  ]
}''',

    'http://admin.test02.qoqa.com/api/v1/shops/100':
r'''{
  "data": [
    {
      "id": 100,
      "name": "Qtest.ch",
      "company": {
        "id": 42,
        "name": "QoQa Services SA"
      },
      "domain": "ch.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_2_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_2_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 2,
      "name": "QoQa.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "ch.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_2_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_2_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 4,
      "name": "Qwine.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qw.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_4_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_4_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_qwine_ch_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qwine_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 7,
      "name": "Qsport.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qs.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_7_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_7_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_qsport_ch_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qsport_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        },
        {
          "name": "de",
          "full": "Deutsch"
        }
      ]
    },
    {
      "id": 9,
      "name": "Qstyle.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qst.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_9_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_9_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        
      ]
    },
    {
      "id": 3,
      "name": "QoQa.fr",
      "company": {
        "id": 2,
        "name": "QoQa Services France SARL"
      },
      "domain": "fr.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_3_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_3_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        {
          "name": "fr",
          "full": "Fran\\u00e7ais"
        }
      ]
    },
    {
      "id": 8,
      "name": "Qwine.fr",
      "company": {
        "id": 2,
        "name": "QoQa Services France SARL"
      },
      "domain": "qwfr.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_8_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_8_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_qwine_ch_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qwine_v1.png"
      },
      "languages": [
        
      ]
    },
    {
      "id": 10,
      "name": "Qooking.ch",
      "company": {
        "id": 1,
        "name": "QoQa Services SA"
      },
      "domain": "qookingch.test02.qoqa.com",
      "medias": {
        "square_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_square_10_v3.png",
        "header_logo": "static.test02.qoqa.com\\\/mobile_applications\\\/logos\\\/shop_header_10_v2.png",
        "soldout_banner": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_mob_fr_v1.png",
        "soldout_variation": "static.test02.qoqa.com\\\/mobile_applications\\\/offers\\\/soldout\\\/soldout_variation_qoqa_v1.png"
      },
      "languages": [
        
      ]
    }
  ],
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
  "language": "qoqacore\\models\\Language",
  "langs": [
    "fr",
    "de"
  ]
}'''
}
