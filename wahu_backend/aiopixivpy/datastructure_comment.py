import dataclasses
from typing import Optional

from .datastructure_illust import PixivUserSummery


@dataclasses.dataclass(slots=True)
class PixivComment:
    """Pixiv 评论的数据结构"""

    cid: int
    comment: str
    date: str
    user: PixivUserSummery
    parent_cid: Optional[int]

