import asyncio
import sqlite3
from pathlib import Path
from random import getrandbits
from time import time
from typing import (AsyncGenerator, AsyncIterable, Callable, Coroutine, Iterable, Optional,
                    Tuple, Union, AsyncIterable)

from ..wahu_core.wahu_cli import AsyncGenPipe

from ..aiopixivpy import IllustDetail
from ..sqlite_tools import ConfigStoredinSqlite, SqliteTableEditor
from ..sqlite_tools.abc import DependingDatabase

from .ib_datastructure import IllustBookmark, IllustBookmarkingConfig, OverwriteMode
from .log_adapter import IllustBookmarkDatabaseLogAdapter
from .logger import logger


async def alist_illusts_piped(
    g: AsyncIterable[list[IllustDetail]],
    ibd: 'IllustBookmarkDatabase',
    pipe: AsyncGenPipe,
    count: int = -1,
    intelligent: bool = False
):
    """
    将一个 `AsyncIterable` 中元素提取到一个 `list` 中
    - `:param count:` 提取的最大元素数量, -1 表示耗尽
    """
    def add_to(illusts: list[IllustDetail]):
        ibd.illusts_te.insert(illusts)
        ibd.bookmarks_te.insert(
            [IllustBookmark(ilst.iid, list(range(ilst.page_count)), int(time()))
            for ilst in illusts]
        )
        pipe.output('\n'.join([f"{ilst.title} - {ilst.iid}" for ilst in illusts]))

    try:
        if intelligent:
            async for item in g:
                if all((ibd.query_detail(ilst.iid) != None for ilst in item)):
                    raise StopAsyncIteration
                add_to(item)

        elif count == -1:
            async for item in g:
                add_to(item)

        else:
            i = 0
            async for item in g:
                add_to(item)
                i += 1
                if i == count:
                    raise StopAsyncIteration

    except StopAsyncIteration:
        pass
    finally:
        pipe.close()


class IllustBookmarkDatabase(DependingDatabase):
    """使用数据库储存收藏的插画及其详细信息，粒度为每张图片"""

    def get_default_config(self) -> IllustBookmarkingConfig:
        cfg = IllustBookmarkingConfig(
            did=getrandbits(16),
            name=self.name,
            description='',
            subscribed_bookmark_uid=[],
            subscribed_user_uid=[],
            subscribe_overwrite='intelligent',
            subscribe_pages=-1
        )
        return cfg

    illusts_te: SqliteTableEditor[IllustDetail] = SqliteTableEditor('illusts', IllustDetail)
    bookmarks_te: SqliteTableEditor[IllustBookmark] = SqliteTableEditor('bookmarks', IllustBookmark)


    config_table_editor: ConfigStoredinSqlite[IllustBookmarkingConfig] = \
        ConfigStoredinSqlite(
            IllustBookmarkingConfig,
            name='config'
    )

    def __init__(self, name: str, db_path: Union[str, Path]):

        self.name: str = name
        self.db_path: Union[Path, str] = db_path

        self.config = self.config_table_editor.v

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

        self.config_table_editor.bind(cur)
        self.config_table_editor.create_if_not()

        if self.config_table_editor.empty:
            self.config_table_editor.insert([self.get_default_config()])

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
    ) -> None:
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

    async def update_subscrip(
        self,
        get_user_illusts: Callable[[int], AsyncGenerator[list[IllustDetail], None]],
        get_user_bookmarks: Callable[[int], AsyncGenerator[list[IllustDetail], None]],
        overwrite: Optional[OverwriteMode] = None,
        page_num: Optional[int] = None
    ) -> tuple[Coroutine[None, None, None], AsyncGenPipe]:
        """
        更新订阅的用户作品和用户收藏
        - `:param get_user_illusts:` 获取用户作品的方法，如 `PixivAPI.user_illusts`
        - `:param get_user_bookmarks:` 获取用户收藏的方法
        - `:delete:` 是否清空以前的记录
        - `:page_num:` 对于每一条订阅，更新的页数. 若提供了，则 `delete` 无效
        每个插画的所有的页都将被收藏
        """

        pipe = AsyncGenPipe()

        cfg = self.config_table_editor.select()[0]

        if page_num is None:
            page_num = cfg.subscribe_pages

        if overwrite is None:
            overwrite = cfg.subscribe_overwrite

        if overwrite == "replace":

            self.log_adapter.info('update_subscrip: 清空数据')

            self.illusts_te.delete()
            self.bookmarks_te.delete()
        
        async def coro():
            assert page_num != None
            coro_list = [
                *(
                    alist_illusts_piped(
                        get_user_illusts(uid),
                        self, pipe, page_num, intelligent=overwrite == "intelligent")
                    for uid in cfg.subscribed_user_uid
                ),
                *(
                    alist_illusts_piped(
                        get_user_bookmarks(uid),
                        self, pipe, page_num, intelligent=overwrite == "intelligent")
                    for uid in cfg.subscribed_bookmark_uid
                )
            ]

            await asyncio.gather(*coro_list)

        return (coro(), pipe)

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


