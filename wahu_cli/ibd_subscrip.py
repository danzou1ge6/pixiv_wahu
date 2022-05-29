import asyncio
import itertools
import time
from typing import TYPE_CHECKING, AsyncIterable, Optional, Type, TypeVar

import click
import toml

from wahu_backend.illust_bookmarking import IllustBookmark

if TYPE_CHECKING:
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

NAME = '插画数据库订阅'
DESCRIPTION = '根据订阅配置文件中记录的用户 ID 更新数据库中插画'


T = TypeVar('T')
async def alist(g: AsyncIterable[T], count: Optional[int] = None) -> list[T]:
    """
    将一个 `AsyncIterable` 中元素提取到一个 `list` 中
    - `:param count:` 提取的最大元素数量
    """

    ret = []

    if count is None:
        try:
            async for item in g:
                ret.append(item)
        except StopAsyncIteration:
            return ret
        finally:
            return ret

    else:
        i = 0
        try:
          async for item in g:
              ret.append(item)
              i += 1

              if i == count:
                  raise StopAsyncIteration
        except StopAsyncIteration:
            return ret
        finally:
            return ret

def mount(wexe: click.Group, wahu_cli_wrap):

    @wexe.command()
    @click.option('--page', '-p', type=int, default=-1, help='每条订阅更新的目录数')
    @click.option(
        '--overwrite/--no-overwrite', '-o/', is_flag=True, help='是否覆盖原有内容')
    @click.option(
        '--user-uid', '-u', type=int, multiple=True, help='手动指定订阅画师的 UID',
        metavar='<user_uid>')
    @click.option(
        '--bookmark-uid', '-b', type=int, multiple=True, help='手动指定订阅收藏的 UID',
        metavar='<bookmark_uid>')
    @click.argument('name', type=str)
    @wahu_cli_wrap
    async def ibd_subscrip(
        cctx: click.Context,
        page: int,
        overwrite: bool,
        user_uid: list[str],
        bookmark_uid: list[str],
        name: str
    ):
        """更新数据库 NAME 的订阅

        如果手动指定了 <user_uid> 或 <bookmark_uid> 中的至少一个，则使用它
        否则从文件 `config.local.ibd_subscrip` 中加载

        配置文件格式 (toml):
            [<name>]
            subscribed_user_uid = [123, 234, 345]
            subscribed_bookmark_uid = [123, 234, 345]
        """

        obj: CliClickCtxObj = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()

        if len(user_uid) == 0 and len(bookmark_uid) == 0:

            conf = wctx.config.original_dict['local']['ibd_subscrip']

            try:
                subs_conf = toml.load(conf)[name]
            except KeyError:
                raise KeyError(f'fatal: {name} 不在订阅配置文件中')

            subs_user_uid = subs_conf.get('subscribed_user_uid', [])
            subs_bm_uid = subs_conf.get('subscribed_bookmark_uid', [])

            pipe.putline(f'订阅的画师: {subs_user_uid}')
            pipe.putline(f'订阅的收藏: {subs_bm_uid}')
        else:
            subs_user_uid = [] if user_uid is None else user_uid
            subs_bm_uid = [] if bookmark_uid is None else bookmark_uid

        if name not in wctx.ilst_bmdbs.keys():
            raise KeyError(f'fatal: {name} 不存在')

        if not wctx.papi.logged_in:
            raise RuntimeError(f'fatal: 未登录 Pixiv')

        coro_list = [
            *(
                alist(wctx.papi.user_illusts(uid), page)
                for uid in subs_user_uid
            ),
            *(
                alist(wctx.papi.user_bookmarks_illusts(uid), page)
                for uid in subs_bm_uid
            )
        ]

        pipe.putline('开始下载详情')
        illusts_lllist = await asyncio.gather(*coro_list)
        # illusts_lllist' s type is tuple[list[list[IllustsDetail]]]

        illusts = list(itertools.chain(*itertools.chain(*illusts_lllist)))

        pipe.putline(f'加入收藏 ID {[ilst.iid for ilst in illusts]}')

        with await wctx.ilst_bmdbs[name](readonly=False) as ibd:

            if overwrite:

                pipe.putline('警告: 清空数据')

                ibd.illusts_te.delete()
                ibd.bookmarks_te.delete()

            ibd.illusts_te.insert(illusts)

            ibd.bookmarks_te.insert(
                [IllustBookmark(ilst.iid, list(range(ilst.page_count)), int(time.time()))
                for ilst in illusts]
            )

