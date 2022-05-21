import dataclasses

from ..sqlite_tools.abc import DatabaseRow
from ..sqlite_tools.adapters import IntAdapter, JsonAdapter, StrAdapter


@dataclasses.dataclass
class IllustBookmarkRaw:
    iid: int
    pages: list[int]


class IllustBookmark(IllustBookmarkRaw, DatabaseRow):
    adapters = {
        'iid': IntAdapter,
        'pages': JsonAdapter
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


class IllustBookmarkingConfig(IllustBookmarkingConfigRaw, DatabaseRow):
    adapters = {
        'did': IntAdapter,
        'name': StrAdapter,
        'description': StrAdapter,
        'subscribed_user_uid': JsonAdapter,
        'subscribed_bookmark_uid': JsonAdapter
    }

    keys = list(adapters.keys())

    index = 'did'
