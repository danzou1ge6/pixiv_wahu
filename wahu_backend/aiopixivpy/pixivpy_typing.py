from typing import Literal, TypeAlias


from ..http_typing import HTTPData, URLParams, HTTPHeaders


PixivRestrict: TypeAlias = Literal['public', 'private']
PixivSearchTarget: TypeAlias = Literal["partial_match_for_tags",
                                    "exact_match_for_tags",
                                    "title_and_caption", "keyword"]
PixivSort: TypeAlias = Literal["date_desc", "date_asc", "popular_desc"]
PixivDuration: TypeAlias = Literal["within_last_day", "within_last_week",
                               "within_last_month"]
PixivRecomMode: TypeAlias = Literal[
    "day",
    "week",
    "month",
    "day_male",
    "day_female",
    "week_original",
    "week_rookie"
]
