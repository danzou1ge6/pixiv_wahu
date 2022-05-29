import dataclasses

from ..sqlite_tools.abc import DatabaseRow
from ..sqlite_tools.adapters import IntAdapter, JsonAdapter, StrAdapter


@dataclasses.dataclass
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

