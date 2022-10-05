import dataclasses
import json
from dataclasses import dataclass
from typing import Iterator, NamedTuple

from ..http_typing import JSONItem

from ..sqlite_tools.abc import DatabaseRow
from ..sqlite_tools.adapters import (BoolAdapter, IntAdapter, JsonAdapter,
                                     SqliteAdapter, SqliteStoreType,
                                     StrAdapter)

"""
此模块包含储存插画详情的数据类型 IllustDetail ，以及为将其存入 sqlite 数据库而编写的一些组件
- :class PixivUserSummery: 插画详情中的作者信息
- :class IllustTagList: 插画中的标签
"""


@dataclass(slots=True)
class PixivUserSummery:
    '''保存用户详情的 dataclass 基类'''
    account: str
    uid: int
    is_followed: bool
    name: str
    profile_image: str  # url

    def __hash__(self) -> int:
        return self.uid

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, PixivUserSummery):
            return self.uid == __o.uid
        return False


class PixivUserSummeryAdapter(SqliteAdapter):
    """用 JSON 元组的形式保存"""

    store_type = SqliteStoreType.TEXT

    @staticmethod
    def serialized(u: PixivUserSummery) -> str:
        return json.dumps(dataclasses.astuple(u))

    @staticmethod
    def deserialized(j: str) -> PixivUserSummery:
        return PixivUserSummery(*json.loads(j))


@dataclass(slots=True)
class IllustTag:
    name: str
    translated: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, IllustTag):
            return self.name == __o.name
        return False


class IllustTagListAdapter(SqliteAdapter):
    """用 JSON 列表的形式保存"""

    store_type = SqliteStoreType.TEXT

    @staticmethod
    def serialized(i: list[IllustTag]) -> str:
        return json.dumps([dataclasses.astuple(it) for it in i])

    @staticmethod
    def deserialized(j: str) -> list[IllustTag]:
        return [IllustTag(n, t) for n, t in json.loads(j)]



@dataclass(slots=True)
class IllustDetailRaw:
    '''
    保存插画详情的 dataclass 基类
    定义这个基类是为了防止 `adapters` `keys` `index` 被 `dataclass` 当作 field 处理
    '''
    iid: int
    title: str
    caption: str
    height: int
    width: int
    is_bookmarked: bool
    is_muted: bool
    page_count: int
    restrict: int
    sanity_level: int
    tags: list[IllustTag]
    total_bookmarks: int
    type: str
    total_view: int
    user: PixivUserSummery
    visible: bool
    x_restrict: int
    image_origin: list[str]
    image_large: list[str]
    image_medium: list[str]
    image_sqmedium: list[str]


class IllustDetail(IllustDetailRaw, DatabaseRow):
    """
    继承 IllustDetailRaw ，添加数据库操作相关属性
    - `:member adapters:` 保存类型转换所需要的 Adapters
    - `:member keys:` 键值
    - `:member index:` 在数据库中用作 `PRIMARY KEY` 的属性名
    """

    adapters = {
        'iid': IntAdapter,
        'title': StrAdapter,
        'caption': StrAdapter,
        'height': IntAdapter,
        'width': IntAdapter,
        'is_bookmarked': BoolAdapter,
        'is_muted': BoolAdapter,
        'page_count': IntAdapter,
        'restrict': IntAdapter,
        'sanity_level': IntAdapter,
        'tags': IllustTagListAdapter,
        'total_bookmarks': IntAdapter,
        'type': StrAdapter,
        'total_view': IntAdapter,
        'user': PixivUserSummeryAdapter,
        'visible': BoolAdapter,
        'x_restrict': IntAdapter,
        'image_origin': JsonAdapter,
        'image_large': JsonAdapter,
        'image_medium': JsonAdapter,
        'image_sqmedium': JsonAdapter
    }

    keys = list(adapters.keys())
    index = 'iid'


@dataclass(slots=True)
class TrendingTagIllusts:
    tag: IllustTag
    illust: IllustDetail
