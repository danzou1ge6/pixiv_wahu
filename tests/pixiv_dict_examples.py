import json

illust_dict1 = json.loads(
    """
    {
        "caption": "happybirthday!!♡",
        "create_date": "2017-06-12T00:36:32+09:00",
        "height": 979,
        "id": 63343772,
        "image_urls": {
            "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2017/06/12/00/36/32/63343772_p0_master1200.jpg",
            "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2017/06/12/00/36/32/63343772_p0_master1200.jpg",
            "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2017/06/12/00/36/32/63343772_p0_square1200.jpg"
        },
        "is_bookmarked": true,
        "is_muted": false,
        "meta_pages": [
            {
                "image_urls": {
                    "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2017/06/12/00/36/32/63343772_p0_master1200.jpg",
                    "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2017/06/12/00/36/32/63343772_p0_master1200.jpg",
                    "original": "https://i.pximg.net/img-original/img/2017/06/12/00/36/32/63343772_p0.png",
                    "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2017/06/12/00/36/32/63343772_p0_square1200.jpg"
                }
            },
            {
                "image_urls": {
                    "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2017/06/12/00/36/32/63343772_p1_master1200.jpg",
                    "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2017/06/12/00/36/32/63343772_p1_master1200.jpg",
                    "original": "https://i.pximg.net/img-original/img/2017/06/12/00/36/32/63343772_p1.png",
                    "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2017/06/12/00/36/32/63343772_p1_square1200.jpg"
                }
            }
        ],
        "meta_single_page": {},
        "page_count": 2,
        "restrict": 0,
        "sanity_level": 2,
        "series": null,
        "tags": [
            {
                "name": "リトルバスターズ",
                "translated_name": "little busters"
            },
            {
                "name": "能美クドリャフカ",
                "translated_name": "Kudryavka Noumi"
            },
            {
                "name": "クド",
                "translated_name": "kud"
            },
            {
                "name": "リトバス",
                "translated_name": null
            },
            {
                "name": "littleBusters!",
                "translated_name": null
            },
            {
                "name": "Key",
                "translated_name": null
            },
            {
                "name": "誕生日",
                "translated_name": "birthday"
            },
            {
                "name": "kud",
                "translated_name": null
            },
            {
                "name": "ニーソ",
                "translated_name": "kneesocks"
            },
            {
                "name": "ダブルピース",
                "translated_name": "double peace sign"
            }
        ],
        "title": "クド",
        "tools": [
            "SAI"
        ],
        "total_bookmarks": 1646,
        "total_view": 13587,
        "type": "illust",
        "user": {
            "account": "marumaa",
            "id": 12501110,
            "is_followed": false,
            "name": "maruma@お仕事募集中",
            "profile_image_urls": {
                "medium": "https://i.pximg.net/user-profile/img/2020/04/27/21/48/06/18426862_4307327ae8676106e95591351d4a2fb3_170.png"
            }
        },
        "visible": true,
        "width": 700,
        "x_restrict": 0
    }
    """)


illust_dict2 = json.loads(
    """{
    "caption": "",
    "create_date": "2017-05-27T13:40:27+09:00",
    "height": 1419,
    "id": 63090645,
    "image_urls": {
        "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2017/05/27/13/40/27/63090645_p0_master1200.jpg",
        "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2017/05/27/13/40/27/63090645_p0_master1200.jpg",
        "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2017/05/27/13/40/27/63090645_p0_square1200.jpg"
    },
    "is_bookmarked": true,
    "is_muted": false,
    "meta_pages": [],
    "meta_single_page": {
        "original_image_url": "https://i.pximg.net/img-original/img/2017/05/27/13/40/27/63090645_p0.jpg"
    },
    "page_count": 1,
    "restrict": 0,
    "sanity_level": 4,
    "series": null,
    "tags": [
        {
            "name": "AngelBeats!",
            "translated_name": null
        },
        {
            "name": "みゆきち",
            "translated_name": null
        },
        {
            "name": "入江",
            "translated_name": null
        }
    ],
    "title": "みゆきち",
    "tools": [],
    "total_bookmarks": 132,
    "total_view": 1742,
    "type": "illust",
    "user": {
        "account": "chibiran123",
        "id": 802482,
        "is_followed": false,
        "name": "チビのん☆",
        "profile_image_urls": {
            "medium": "https://i.pximg.net/user-profile/img/2020/01/12/03/26/55/16839465_88e49642a5fe1d958a37466512291150_170.jpg"
        }
    },
    "visible": true,
    "width": 1000,
    "x_restrict": 0
}
    """
)

user_detail_dict = json.loads(
"""
{
    "user": {
        "id": 340139,
        "name": "SALT",
        "account": "seren_1121",
        "profile_image_urls": {
            "medium": "https://i.pximg.net/user-profile/img/2012/08/14/23/43/00/5007939_895e2d82088b2c31ed90d2054463117d_170.jpg"
        },
        "comment": "女の子を描くのが大好き♪評価やブクマ、タグ",
        "is_followed": false
    },
    "profile": {
        "webpage": null,
        "gender": "",
        "birth": "",
        "birth_day": "",
        "birth_year": 0,
        "region": "",
        "address_id": 0,
        "country_code": "",
        "job": "",
        "job_id": 0,
        "total_follow_users": 1065,
        "total_mypixiv_users": 38,
        "total_illusts": 54,
        "total_manga": 2,
        "total_novels": 0,
        "total_illust_bookmarks_public": 3702,
        "total_illust_series": 0,
        "total_novel_series": 0,
        "background_image_url": "https://i.pximg.net/c/1200x600_90_a2_g5/background/img/2019/12/28/00/36/26/340139_ce528df04cc0755189409e39eaaad1c8_master1200.jpg",
        "twitter_account": "",
        "twitter_url": null,
        "pawoo_url": null,
        "is_premium": false,
        "is_using_custom_profile_image": true
    },
    "profile_publicity": {
        "gender": "public",
        "region": "public",
        "birth_day": "public",
        "birth_year": "public",
        "job": "public",
        "pawoo": true
    },
    "workspace": {
        "pc": "",
        "monitor": "",
        "tool": "",
        "scanner": "",
        "tablet": "",
        "mouse": "",
        "printer": "",
        "desktop": "",
        "music": "",
        "desk": "",
        "chair": "",
        "comment": "",
        "workspace_image_url": null
    }
}
"""
)

user_preview_dict = json.loads(
    """
        {
            "user": {
                "id": 6239377,
                "name": "X-red flower",
                "account": "270636661",
                "profile_image_urls": {
                    "medium": "https://i.pximg.net/user-profile/img/2015/05/15/19/43/18/9366370_e6d292fb9fa0b02d840c5385ed2bc457_170.jpg"
                },
                "is_followed": false
            },
            "illusts": [
                {
                    "id": 89216300,
                    "title": "摸鱼",
                    "type": "illust",
                    "image_urls": {
                        "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2021/04/17/23/09/46/89216300_p0_square1200.jpg",
                        "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2021/04/17/23/09/46/89216300_p0_master1200.jpg",
                        "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2021/04/17/23/09/46/89216300_p0_master1200.jpg"
                    },
                    "caption": "给朋友画的图",
                    "restrict": 0,
                    "user": {
                        "id": 6239377,
                        "name": "X-red flower",
                        "account": "270636661",
                        "profile_image_urls": {
                            "medium": "https://i.pximg.net/user-profile/img/2015/05/15/19/43/18/9366370_e6d292fb9fa0b02d840c5385ed2bc457_170.jpg"
                        },
                        "is_followed": false
                    },
                    "tags": [
                        {
                            "name": "女の子",
                            "translated_name": null
                        }
                    ],
                    "tools": [
                        "SAI",
                        "Photoshop"
                    ],
                    "create_date": "2021-04-17T23:09:46+09:00",
                    "page_count": 2,
                    "width": 6000,
                    "height": 7000,
                    "sanity_level": 2,
                    "x_restrict": 0,
                    "series": null,
                    "meta_single_page": {},
                    "meta_pages": [
                        {
                            "image_urls": {
                                "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2021/04/17/23/09/46/89216300_p0_square1200.jpg",
                                "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2021/04/17/23/09/46/89216300_p0_master1200.jpg",
                                "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2021/04/17/23/09/46/89216300_p0_master1200.jpg",
                                "original": "https://i.pximg.net/img-original/img/2021/04/17/23/09/46/89216300_p0.jpg"
                            }
                        },
                        {
                            "image_urls": {
                                "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2021/04/17/23/09/46/89216300_p1_square1200.jpg",
                                "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2021/04/17/23/09/46/89216300_p1_master1200.jpg",
                                "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2021/04/17/23/09/46/89216300_p1_master1200.jpg",
                                "original": "https://i.pximg.net/img-original/img/2021/04/17/23/09/46/89216300_p1.jpg"
                            }
                        }
                    ],
                    "total_view": 7149,
                    "total_bookmarks": 802,
                    "is_bookmarked": false,
                    "visible": true,
                    "is_muted": false
                },
                {
                    "id": 78476680,
                    "title": "*<|:-) ",
                    "type": "illust",
                    "image_urls": {
                        "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2019/12/25/11/26/45/78476680_p0_square1200.jpg",
                        "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2019/12/25/11/26/45/78476680_p0_master1200.jpg",
                        "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2019/12/25/11/26/45/78476680_p0_master1200.jpg"
                    },
                    "caption": "圣诞快乐 送给徐小(ˉ(∞)ˉ)",
                    "restrict": 0,
                    "user": {
                        "id": 6239377,
                        "name": "X-red flower",
                        "account": "270636661",
                        "profile_image_urls": {
                            "medium": "https://i.pximg.net/user-profile/img/2015/05/15/19/43/18/9366370_e6d292fb9fa0b02d840c5385ed2bc457_170.jpg"
                        },
                        "is_followed": false
                    },
                    "tags": [
                        {
                            "name": "女の子",
                            "translated_name": null
                        },
                        {
                            "name": "猫と女の子",
                            "translated_name": null
                        },
                        {
                            "name": "オリジナル1000users入り",
                            "translated_name": null
                        }
                    ],
                    "tools": [
                        "SAI",
                        "Photoshop"
                    ],
                    "create_date": "2019-12-25T11:26:45+09:00",
                    "page_count": 1,
                    "width": 1702,
                    "height": 2798,
                    "sanity_level": 2,
                    "x_restrict": 0,
                    "series": null,
                    "meta_single_page": {
                        "original_image_url": "https://i.pximg.net/img-original/img/2019/12/25/11/26/45/78476680_p0.jpg"
                    },
                    "meta_pages": [],
                    "total_view": 15077,
                    "total_bookmarks": 2543,
                    "is_bookmarked": false,
                    "visible": true,
                    "is_muted": false
                },
                {
                    "id": 70465152,
                    "title": "11TH",
                    "type": "illust",
                    "image_urls": {
                        "square_medium": "https://i.pximg.net/c/360x360_70/img-master/img/2018/08/31/01/41/03/70465152_p0_square1200.jpg",
                        "medium": "https://i.pximg.net/c/540x540_70/img-master/img/2018/08/31/01/41/03/70465152_p0_master1200.jpg",
                        "large": "https://i.pximg.net/c/600x1200_90/img-master/img/2018/08/31/01/41/03/70465152_p0_master1200.jpg"
                    },
                    "caption": "君が生まれた日をいくつも数えては<br />灯をともしてそっと吹き消しておくれ<br />(*^▽^*)~~",
                    "restrict": 0,
                    "user": {
                        "id": 6239377,
                        "name": "X-red flower",
                        "account": "270636661",
                        "profile_image_urls": {
                            "medium": "https://i.pximg.net/user-profile/img/2015/05/15/19/43/18/9366370_e6d292fb9fa0b02d840c5385ed2bc457_170.jpg"
                        },
                        "is_followed": false
                    },
                    "tags": [
                        {
                            "name": "初音ミク",
                            "translated_name": null
                        },
                        {
                            "name": "VOCALOID",
                            "translated_name": null
                        },
                        {
                            "name": "初音ミク生誕祭2018",
                            "translated_name": null
                        },
                        {
                            "name": "マジカルミライ2017",
                            "translated_name": null
                        },
                        {
                            "name": "VOCALOID10000users入り",
                            "translated_name": null
                        },
                        {
                            "name": "なにこれ素敵",
                            "translated_name": null
                        },
                        {
                            "name": "Birthday",
                            "translated_name": null
                        },
                        {
                            "name": "サイハイブーツ",
                            "translated_name": null
                        }
                    ],
                    "tools": [
                        "SAI",
                        "Photoshop"
                    ],
                    "create_date": "2018-08-31T01:41:03+09:00",
                    "page_count": 1,
                    "width": 2400,
                    "height": 1625,
                    "sanity_level": 2,
                    "x_restrict": 0,
                    "series": null,
                    "meta_single_page": {
                        "original_image_url": "https://i.pximg.net/img-original/img/2018/08/31/01/41/03/70465152_p0.jpg"
                    },
                    "meta_pages": [],
                    "total_view": 92547,
                    "total_bookmarks": 17730,
                    "is_bookmarked": false,
                    "visible": true,
                    "is_muted": false
                }
            ],
            "novels": [],
            "is_muted": false
        }
    """
)
