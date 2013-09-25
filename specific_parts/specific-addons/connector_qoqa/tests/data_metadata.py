# -*- coding: utf-8 -*-

"""
Responses returned by the QoQa Web-Services

Use 'en' for the language instead of 'fr'
to be sure that the tests are working even if the
'fr' lang is not installed.
"""

qoqa_shops = {
    'http://test02.qoqa.com/api/v1/en/shops/':
    '''{"data": [
            {
                "id": 1,
                "name": "Qtest.ch",
                "company": {
                    "id": 42,
                    "name": "QoQa Services SA"
                },
                "domain": "qtest.ch",
                "medias": {
                    "square_logo": "static.qoqa.ch/mobile_applications/logos/shop_square_1_v1.png",
                    "header_logo": "static.qoqa.ch/mobile_applications/logos/shop_header_1_v1.png",
                    "soldout_banner": "static.qoqa.ch/mobile_applications/offers/soldout/soldout_mob_de_v1.png"
                },
                "languages": [
                    {
                        "name": "fr",
                        "full": "Français"
                    }
                ]
            }
    ]}'''
}
