import dataclasses

from ..sqlite_tools.abc import DatabaseRow
from ..sqlite_tools.adapters import BoolAdapter, IntAdapter, StrAdapter
from .datastructure_illust import IllustDetail, PixivUserSummery


@dataclasses.dataclass(slots=True)
class PixivUserDetailRaw:
    uid: int
    account: str
    name: str
    profile_image: str
    is_followed: bool

    comment: str

    total_followers: int
    total_mypixiv_users: int
    total_illusts: int
    total_manga: int
    total_novels: int
    total_bookmarked_illust: int
    background_image: str


class PixivUserDetail(PixivUserDetailRaw, DatabaseRow):
    """保存 Pixiv 用户的详细信息"""

    adapters = {
        'uid': IntAdapter,
        'account': StrAdapter,
        'name': StrAdapter,
        'profile_image': StrAdapter,
        'is_followed': BoolAdapter,
        'comment': StrAdapter,
        'total_followers': IntAdapter,
        'total_mypixiv_users': IntAdapter,
        'total_illusts': IntAdapter,
        'total_manga': IntAdapter,
        'total_novels': IntAdapter,
        'total_bookmarked_illust': IntAdapter,
        'background_image': StrAdapter
    }

    keys = list(adapters.keys())
    index = 'uid'



@dataclasses.dataclass(slots=True)
class PixivUserPreview:
    """搜索用户、获取相关用户时返回的数据结构"""

    user_summery: PixivUserSummery
    illusts: list[IllustDetail]
