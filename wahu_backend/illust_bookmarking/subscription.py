from typing import Literal, Optional
import toml
import asyncio
import itertools
from pathlib import Path
from dataclasses import dataclass

from . import IllustBookmarkDatabase
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from ..aiopixivpy import PixivAPI
from ..async_util import alist
from ..wahu_config.config_exceptions import ConfigLoadKeyError


@dataclass
class IllustsSubscription:
    """一条订阅. `work` 类型表示订阅 `uid` 的作品，而 `bookmark` 类型表示订阅 `uid`的收藏"""
    s_type: Literal["work", "bookmark"]
    uid: int

    def __init__(self, s_type: Literal["work", "bookmark"], uid: str):
        self.s_type = s_type
        self.uid = -1 if uid == 'me' else int(uid)

@dataclass
class DatabaseSubscription:
    """一个数据库的一组订阅"""
    name: str
    overwrite: bool  # 是否写入订阅前覆盖数据库
    page: int  # 一次拉取插画的页数 (Pixiv 服务器一页返回约 30 条)
    subscriptions: list[IllustsSubscription]

class SubscriptionError(Exception):
    pass

class SubscriptionFileNotExist(SubscriptionError):
    file: Path
    def __init__(self, file: Path):
        self.file = file
    def __str__(self):
        return f"订阅文件 {self.file} 不存在"

class SubscriptionFileBad(SubscriptionError):
    pass

class SubscriptionManager:
    """管理一组订阅
    """
    def __init__(
        self,
        sub_file: Path,
        papi: PixivAPI,
        ibds: dict[str, DatabaseContextManager[IllustBookmarkDatabase]]
    ):
        self.sub_file = sub_file
        self.papi = papi
        self.ibds = ibds

        self.load_subs()  # in case 前端需要使用
    
    def load_subs(self):
        """
        从配置文件中读取订阅. 凡 `uid` 域为"me" 的项，会用 -1 替代；uid=-1 在调用 `update_subscriptions`
        时会被替换成自己的 uid
        """
        if not self.sub_file.exists():
            raise SubscriptionFileNotExist(self.sub_file)
        
        subs_conf = toml.load(self.sub_file)

        try:
            self.subscriptions = {
                name: DatabaseSubscription(
                    name=name, overwrite=entry['overwrite'], page=int(entry['page']),
                    subscriptions=[IllustsSubscription(s_type=sub['type'], uid=sub['uid']) for sub in entry['subscriptions']]
                )
                for name, entry in subs_conf.items()
            }
        except KeyError as e:
            raise SubscriptionFileBad(str(e))

    
    async def update_subscriptions(
        self,
        name: str,
        pages: Optional[int]=None,
        overwrite: Optional[bool]=None,
        work_uids: list[int]=[],
        bookmark_uids: list[int]=[]
    ):
        """
        更新某个数据库的订阅.

        执行时会先从配置文件中读取订阅.

        @param name: 数据库的名称
        @param pages: 下载的页数. 未指定则使用订阅配置中的设定
        @param overwrite: 写入新插画前是否清空数据库. 未指定则使用订阅配置中的设定
        @param work_uids, bookmark_uids: 拉取来源，详见 IllustsSubscription. 空列表则使用订阅配置中的设定
        """
        self.load_subs()

        if name not in self.subscriptions.keys():
            raise KeyError(f"没有插画数据库 {name} 的订阅")
        
        db_subs = self.subscriptions[name]

        if pages is None:
            pages = db_subs.page
        
        if overwrite is None:
            overwrite = db_subs.overwrite
        
        if len(work_uids) == 0:
            work_uids = [sub.uid for sub in db_subs.subscriptions if sub.s_type == "work"]
            if -1 in work_uids and self.papi.account_session is None:
                raise RuntimeError("未登录 Pixiv")  # 一般调用此函数时已经登录
            work_uids = [
                uid if uid != -1 else self.papi.account_session.user_id for uid in work_uids]  # type: ignore
        
        if len(bookmark_uids) == 0:
            bookmark_uids = [sub.uid for sub in db_subs.subscriptions if sub.s_type == "bookmark"]
            if -1 in work_uids and self.papi.account_session is None:
                raise RuntimeError("未登录 Pixiv")  # 一般调用此函数时已经登录
            bookmark_uids = [
                uid if uid != -1 else self.papi.account_session.user_id for uid in bookmark_uids]  # type: ignore

        coro_list = [
            *(
                alist(self.papi.user_illusts(uid), pages)
                for uid in work_uids
            ),
            *(
                alist(self.papi.user_bookmarks_illusts(uid), pages)
                for uid in bookmark_uids
            )
        ]

        illusts_lllist = await asyncio.gather(*coro_list)
        # type of above expression is: tuple[list[list[IllustDetail]]]
        
        illusts = list(itertools.chain(*itertools.chain(*illusts_lllist)))

        if name not in self.ibds:
            raise KeyError(f"插画数据库 {name} 不存在")

        with await self.ibds[name](readonly=False) as ibd:
            if overwrite:
                ibd.illusts_te.delete()
                ibd.bookmarks_te.delete()
            ibd.illusts_te.insert(illusts)

            for ilst in illusts:
                await ibd.set_bookmark(ilst.iid, list(range(ilst.page_count)))

