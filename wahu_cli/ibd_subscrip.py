import asyncio
import itertools
from typing import TYPE_CHECKING, AsyncIterable, Optional, TypeVar

import click
import toml

from wahu_backend.illust_bookmarking import IllustBookmark

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap


IGNORE = True  # 不被自动加载


def mount(parent_group: click.Group):

    @parent_group.command()
    @click.option('--page', '-p', type=int, default=None, help='每条订阅更新的目录数')
    @click.option(
        '--overwrite/--no-overwrite', '-o/', is_flag=None, help='是否覆盖原有内容')
    @click.option(
        '--work-uid', '-u', type=int, multiple=True, help='手动指定订阅画师作品的 UID',
        metavar='<user_uid>')
    @click.option(
        '--bookmark-uid', '-b', type=int, multiple=True, help='手动指定订阅收藏的 UID',
        metavar='<bookmark_uid>')
    @click.argument('name', type=str)
    @wahu_cli_wrap
    async def subscrip(
        cctx: click.Context,
        page: Optional[int],
        overwrite: Optional[bool],
        work_uid: list[int],
        bookmark_uid: list[int],
        name: str
    ):
        """更新数据库 NAME 的订阅

        如果手动指定了 <user_uid> 或 <bookmark_uid> 中的至少一个，则使用它
        否则从文件 `config.local.ibd_subscrip` 中加载

        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        if name not in obj.wctx.ilst_bmdbs.keys():
            raise KeyError(f'fatal: 数据库 {name} 不存在')

        if overwrite:
            pipe.putline("警告：将删除数据库中原有插画")

            if await pipe.get(prefix='继续[y/*]?', echo=False) != 'y':
                return
        
        await wctx.ibdsub_man.update_subscriptions(
            name=name, pages=page, overwrite=overwrite,
            work_uids=list(work_uid), bookmark_uids=list(bookmark_uid)
        )

        


