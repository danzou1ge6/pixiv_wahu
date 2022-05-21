from itertools import chain
from typing import NamedTuple

from fuzzywuzzy import process as fwp

from ..aiopixivpy.datastructure_illust import IllustTag
from .illust_bookmark_database import IllustBookmarkDatabase


class ItemToMatch(NamedTuple):
    iid: int
    content: str | list[str]

class MatchResult(NamedTuple):
    iid: int
    score: int


def slice_str(s: str, length: int) -> list[str]:
    return [
        s[begin:begin+length] for begin in range(0, len(s) - length + 1)
    ]

def match_keyword(items: list[ItemToMatch], keyword: str, cutoff: int
) -> list[MatchResult]:
    """将 items 匹配 keyword ，然后返回排序后的匹配结果"""

    result_list = []

    for item in items:
        if isinstance(item.content, str):
            slices = slice_str(item.content, len(keyword))
        else:
            slices = list(chain(
                *(slice_str(c, len(keyword)) for c in item.content)
            ))

        fw_result = fwp.extractBests(
            keyword,
            slices,
            scorer=fwp.fuzz.token_sort_ratio,
            score_cutoff=cutoff
        )

        if len(fw_result) != 0:
            score = max((r[1] for r in fw_result))
            result_list.append(MatchResult(item.iid, score))

    return list(sorted(result_list, key=(lambda x: x[1]), reverse=True))


class IllustBookmarkDatabaseQueryMixin(IllustBookmarkDatabase):

    def query_title(self, keyword: str, cutoff: int=80) -> list[MatchResult]:
        items = [
            ItemToMatch(iid, title)
            for iid, title in self.illusts_te.select_cols(
                cols=['iid', 'title']
            )
        ]

        return match_keyword(items, keyword, cutoff=cutoff)

    def query_caption(self, keyword: str, cutoff: int=80) -> list[MatchResult]:
        items = [
            ItemToMatch(iid, caption)
            for iid, caption in self.illusts_te.select_cols(
                cols=['iid', 'caption']
            )
        ]

        return match_keyword(items, keyword, cutoff=cutoff)

    def query_username(self, keyword: str, cutoff: int=80) -> list[MatchResult]:
        items = [
            ItemToMatch(iid, user.name)
            for iid, user in self.illusts_te.select_cols(
                cols=['iid', 'user']
            )
        ]

        return match_keyword(items, keyword, cutoff=cutoff)

    def query_tag(self, keyword: str, cutoff: int=80) -> list[MatchResult]:
        items = [
            ItemToMatch(
                iid,
                [tag.name for tag in tags] + \
                    [tag.translated
                    for tag in tags if tag.translated is not None]
            )
            for iid, tags in self.illusts_te.select_cols(
                cols=['iid', 'tags']
            )
        ]

        return match_keyword(items, keyword, cutoff=cutoff)

    def query_uid(self, uid: int) -> list[int]:
        items = self.illusts_te.select_cols(
            cols=['iid', 'user']
        )

        return [iid for iid, user in items if user.uid == uid]

