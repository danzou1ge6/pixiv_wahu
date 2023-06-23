import dataclasses
from typing import Literal

from ..sqlite_tools.abc import DatabaseRow
from ..sqlite_tools.adapters import IntAdapter, JsonAdapter, StrAdapter, BoolAdapter


@dataclasses.dataclass(slots=True)
class IllustBookmarkRaw:
    iid: int
    pages: list[int]
    add_timestamp: int  # 单位为秒


class IllustBookmark(IllustBookmarkRaw, DatabaseRow):
    adapters = {
        'iid': IntAdapter,
        'pages': JsonAdapter,
        'add_timestamp': IntAdapter
    }

    keys = list(adapters.keys())

    index = 'iid'

    def as_fids(self):
        return [f'{self.iid}-{p}' for p in self.pages]

# 覆写模式
# intelligent: 当遇到一页插画，其中所有插画都存在于数据库中，则停止拉取下面几页
# append     : 拉取指定页数的插画并追加到数据库
# replace    : 删除原有数据，然后拉取指定页数的插画并追加到数据库
OverwriteMode = Literal["intelligent", "append", "replace"]

@dataclasses.dataclass
class IllustBookmarkingConfigRaw:
    did: int  # Database ID
    name: str
    description: str
    subscribed_user_uid: list[int]
    subscribed_bookmark_uid: list[int]
    subscribe_overwrite: OverwriteMode
    subscribe_pages: int


class IllustBookmarkingConfig(IllustBookmarkingConfigRaw, DatabaseRow):
    adapters = {
        'did': IntAdapter,
        'name': StrAdapter,
        'description': StrAdapter,
        'subscribed_user_uid': JsonAdapter,
        'subscribed_bookmark_uid': JsonAdapter,
        'subscribe_overwrite': StrAdapter,
        'subscribe_pages': IntAdapter
    }

    keys = list(adapters.keys())

    index = 'did'

