import dataclasses

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


@dataclasses.dataclass
class IllustBookmarkingConfigRaw:
    did: int  # Database ID
    name: str
    description: str
    subscribed_user_uid: list[int]
    subscribed_bookmark_uid: list[int]
    subscribe_overwrite: bool
    subscribe_pages: int


class IllustBookmarkingConfig(IllustBookmarkingConfigRaw, DatabaseRow):
    adapters = {
        'did': IntAdapter,
        'name': StrAdapter,
        'description': StrAdapter,
        'subscribed_user_uid': JsonAdapter,
        'subscribed_bookmark_uid': JsonAdapter,
        'subscribe_overwrite': BoolAdapter,
        'subscribe_pages': IntAdapter
    }

    keys = list(adapters.keys())

    index = 'did'

