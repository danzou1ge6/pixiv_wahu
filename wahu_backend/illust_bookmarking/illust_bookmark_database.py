import asyncio
import itertools
import sqlite3
from pathlib import Path
from random import getrandbits
from time import time
from typing import (AsyncGenerator, Callable, Coroutine, Iterable, Optional,
                    Tuple, Union)

from ..aiopixivpy import IllustDetail
from ..sqlite_tools import SqliteTableEditor
from ..sqlite_tools.abc import DependingDatabase

from .aitertools import alist
from .ib_datastructure import IllustBookmark
from .log_adapter import IllustBookmarkDatabaseLogAdapter
from .logger import logger


class IllustBookmarkDatabase(DependingDatabase):
    """使用数据库储存收藏的插画及其详细信息，粒度为每张图片"""

    illusts_te: SqliteTableEditor[IllustDetail] = SqliteTableEditor('illusts', IllustDetail)
    bookmarks_te: SqliteTableEditor[IllustBookmark] = SqliteTableEditor('bookmarks', IllustBookmark)

    def __init__(self, name: str, db_path: Union[str, Path]):

        self.name: str = name
        self.db_path: Union[Path, str] = db_path

        self.db_con: sqlite3.Connection

        self.log_adapter = IllustBookmarkDatabaseLogAdapter(self.name, logger)

        self.log_adapter.info('inti: 名称=%s' % name)

    def connect(self) -> None:
        """连接数据库，并创建所有表，并确保配置被初始化了"""

        self.db_con = sqlite3.connect(self.db_path)
        cur = self.db_con.cursor()

        self.illusts_te.bind(cur)
        self.illusts_te.create_if_not()

        self.bookmarks_te.bind(cur)
        self.bookmarks_te.create_if_not()

    def close(self, commit: bool=True) -> None:

        if commit:
            self.db_con.commit()
        self.db_con.close()

    def _del(self, iid: int) -> Tuple[bool, bool]:
        """
        删除 `iid` 的详情和收藏信息
        - `:return:` 返回的两个 `bool` 分别表示 `illusts` 和 `bookmarks` 表中是否执行了删除
        """

        if self.illusts_te.has(iid):
            self.illusts_te.delete([iid])
            flag1 = True
        else:
            flag1 = False

        if self.bookmarks_te.has(iid):
            self.bookmarks_te.delete([iid])
            flag2 = True
        else:
            flag2 = False

        return flag1, flag2

    async def set_bookmark(
        self,
        iid: int,
        pages: list[int],
        get_detail: Optional[Callable[[int],
                                      Coroutine[None, None, IllustDetail]]] = None
    ) -> Tuple[bool, bool]:
        """
        设置 `iid` 收藏的页数
        - `:param iid:` 插画 ID
        - `:param pages:` 页数，从 0 开始数. 注意，此处不对 `pages` 的范围进行校验
        - `:param get_detail:` 获取详情的方法，如果提供了则通过调用此函数获取详情
        - `:return:` 返回的两个 `bool` 分别表示：  `illusts` 是否被更新；
                     `bookmarks` 表中是否新建条目或者删除条目
        """

        if pages == []:
            flag1, flag2 = self._del(iid)
            self.log_adapter.info('set_bookmark: iid=%s 删除'
                                  % iid)
            return flag1, flag2

        if self.illusts_te.has(iid):
            flag1 = False
        else:
            if get_detail is not None:
                detail = await get_detail(iid)
                self.illusts_te.insert([detail])
                flag1 = True
            else:
                flag1 = False

        if self.bookmarks_te.has(iid):
            self.bookmarks_te.update(iid, pages=pages)
            flag2 = False
        else:
            self.bookmarks_te.insert([IllustBookmark(iid, pages, int(time()))])
            flag2 = True

        self.log_adapter.info('set_bookmark: iid=%s ，收藏 %s 页'
                              % (iid, pages))

        return flag1, flag2

    async def update_detail(
        self,
        get_detail: Callable[[int], Coroutine[None, None, IllustDetail]],
        update_all: bool = False
    ) -> list[IllustDetail]:
        """
        更新插画详情. 通过 `get_detail` 获得所有 `bookmarks` 表中出现的插画 ID 的详情
        - `:param get_detail:` 获取插画详情的方法
        - `:param update_all:` 若设置为假，仅 `illusts` 表中未出现的插画会被更新
        """

        to_update_iids: Iterable[int] = list(zip(
            *self.bookmarks_te.select_cols(cols=['iid'])))[0]

        if not update_all:
            to_update_iids = filter(
                lambda iid: not self.illusts_te.has(iid),
                to_update_iids
            )

        to_update_iids = list(to_update_iids)
        self.log_adapter.info('update_detail: 尝试更新 ID %s 的详情' % to_update_iids)

        coro_list = [
            get_detail(iid) for iid in to_update_iids
        ]

        detail_list = await asyncio.gather(*coro_list)

        self.illusts_te.insert(detail_list)

        return list(detail_list)

    def query_detail(self, iid: int) -> Optional[IllustDetail]:
        """在数据库中查询 `iid` 的详情，若无则返回 `None`"""

        ilst = self.illusts_te.select(iid)

        if ilst == []:
            return None
        else:
            return ilst[0]

    def query_bookmark(self, iid: int) -> Optional[IllustBookmark]:
        """在数据库中查找 `iid` 的收藏条目，若无则返回 `None`"""

        ib = self.bookmarks_te.select(iid)

        if ib == []:
            return None
        else:
            return ib[0]

    def all_illusts(self) -> list[IllustDetail]:
        """读出所有插画详情"""

        return self.illusts_te.select()

    def all_bookmarks(self) -> list[IllustBookmark]:
        """读出所有收藏，按添加时间排序"""

        bms = self.bookmarks_te.select()
        bms.sort(key=lambda ilst: ilst.add_timestamp, reverse=True)
        return bms

    def filter_restricted(self) -> list[int]:
        """过滤出已被作者删除的插画"""

        cols = self.illusts_te.select_cols(cols=['iid', 'restrict'])

        return [iid for iid, res in cols if res == 2]

