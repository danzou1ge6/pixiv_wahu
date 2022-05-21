from typing import Any
from .datastructure_illust import IllustDetail, IllustTag, PixivUserSummery
from .datastructure_comment import PixivComment
from .datastructure_user import PixivUserDetail

PIXIV_IMAGE_SERVER = 'https://i.pximg.net'


def process_pixiv_user_summery_dict(pixiv_dict: dict[str, Any]) -> PixivUserSummery:
    """
    转换 Pixiv 返回的用户信息
    - `:param pixiv_dict:` 包含在插画详情、画师搜索结果、评论等字典中，字典键值常为 `user`
    """
    pus = PixivUserSummery(
        pixiv_dict['account'], pixiv_dict['id'],
        pixiv_dict.get('is_followed', False), pixiv_dict['name'],
        pixiv_dict['profile_image_urls']['medium'].replace(
            PIXIV_IMAGE_SERVER, ''
        )
    )
    return pus

def process_pixiv_illust_dict(pixiv_dict: dict[str, Any]) -> IllustDetail:
    """转换 Pixiv 返回的插画详情"""

    # 提取图片链接
    if pixiv_dict['page_count'] == 1:
        image_origin = [pixiv_dict['meta_single_page']['original_image_url']]
        image_medium = [pixiv_dict['image_urls']['medium']]
        image_large = [pixiv_dict['image_urls']['large']]
        image_sqmedium = [pixiv_dict['image_urls']['square_medium']]
    else:
        image_origin = [
            p['image_urls']['original'] for p in pixiv_dict['meta_pages']
        ]
        image_medium = [
            p['image_urls']['medium'] for p in pixiv_dict['meta_pages']
        ]
        image_large = [
            p['image_urls']['large'] for p in pixiv_dict['meta_pages']
        ]
        image_sqmedium = [
            p['image_urls']['square_medium'] for p in pixiv_dict['meta_pages']
        ]

    # 删去链接中的 `https://i.pximg.net`
    image_origin = [
        url.replace(PIXIV_IMAGE_SERVER, '') for url in image_origin
    ]
    image_medium = [
        url.replace(PIXIV_IMAGE_SERVER, '') for url in image_medium
    ]
    image_large = [url.replace(PIXIV_IMAGE_SERVER, '') for url in image_large]
    image_sqmedium = [
        url.replace(PIXIV_IMAGE_SERVER, '') for url in image_sqmedium
    ]

    pus = process_pixiv_user_summery_dict(pixiv_dict['user'])

    idt = (pixiv_dict['id'], pixiv_dict['title'], pixiv_dict.get('caption', ''),
           pixiv_dict.get('height', 0), pixiv_dict.get('width', 0),
           pixiv_dict['is_bookmarked'], pixiv_dict.get('is_muted', False),
           pixiv_dict['page_count'], pixiv_dict['restrict'],
           pixiv_dict['sanity_level'],
           [
               IllustTag(tag['name'], tag['translated_name'])
               for tag in pixiv_dict['tags']
           ],
           pixiv_dict['total_bookmarks'], pixiv_dict['type'],
           pixiv_dict['total_view'],
           pus,
           pixiv_dict.get('visible', False), pixiv_dict['x_restrict'], image_origin,
           image_large, image_medium, image_sqmedium)


    return IllustDetail(*idt)



def process_pixiv_user_detail_dict(pixiv_dict: dict[str, Any]) -> PixivUserDetail:
    """转换 Pixiv 返回的用户详情，仅在接口 `user_detail` 中出现"""

    bg_image_url = pixiv_dict['profile']['background_image_url']
    if bg_image_url is not None:
        bg_image_url = bg_image_url.replace(PIXIV_IMAGE_SERVER, '')
    else:
        bg_image_url = ''

    pud = PixivUserDetail(
        pixiv_dict['user']['id'],
        pixiv_dict['user']['account'],
        pixiv_dict['user']['name'],
        pixiv_dict['user']['profile_image_urls']['medium'].replace(
            PIXIV_IMAGE_SERVER, ''
        ),
        pixiv_dict['user'].get('is_followed', False),
        pixiv_dict['user'].get('comment', ''),
        pixiv_dict['profile']['total_follow_users'],
        pixiv_dict['profile']['total_mypixiv_users'],
        pixiv_dict['profile']['total_illusts'],
        pixiv_dict['profile']['total_manga'],
        pixiv_dict['profile']['total_novels'],
        pixiv_dict['profile']['total_illust_bookmarks_public'],
        bg_image_url
    )

    return pud


def process_pixiv_comment_dict(pixiv_dict: dict[str, Any]) -> PixivComment:
    """转换 Pixiv 返回的评论"""

    pc = pixiv_dict.get('parent_comment', {})
    if pc != {}:
        pcid = pc['id']
    else:
        pcid = None

    return PixivComment(
        pixiv_dict['id'],
        pixiv_dict['comment'],
        pixiv_dict['date'],
        process_pixiv_user_summery_dict(pixiv_dict['user']),
        pcid
    )
