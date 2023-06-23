import argparse
import dataclasses
import json
from pathlib import Path
import asyncio
from typing import TYPE_CHECKING, Literal, Optional, Type, TypeVar, AsyncGenerator

import click

from ..aiopixivpy import IllustDetail, PixivUserSummery, IllustTag
from ..illust_bookmarking import IllustBookmark, IllustBookmarkDatabase, IllustBookmarkingConfig
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from ..wahu_core.wahu_cli import AsyncGenPipe
from ..wahu_core import (GenericWahuMethod, WahuArguments, WahuContext,
                         wahu_methodize)
from ..wahu_core.core_exceptions import WahuRuntimeError
from .lib_logger import logger
from .lib_modded_argparser import ArgumentParser

if TYPE_CHECKING:
    from . import WahuMethods

RT = TypeVar('RT')  # Return Type


async def _check_db_name(
    m: GenericWahuMethod[RT],
    cls: Type['WahuMethods'],
    args: WahuArguments,
    ctx: WahuContext
) -> RT:
    """检查数据库名的中间件"""

    if 'name' not in args:
        raise WahuRuntimeError(f'_check_db_name：未提供数据库名')

    if args.name not in ctx.ilst_bmdbs.keys():
        raise WahuRuntimeError(f'_check_db_name: 数据库名 {args.name} 不在上下文中')

    return await m(cls, args, ctx)


def create_ibd_query_parser() -> argparse.ArgumentParser:
    parser = ArgumentParser(prog='', exit_on_error=False)

    parser.add_argument('keyword', type=str, nargs='?')

    parser.add_argument(
        '-c', '--cutoff', type=int, default=80, help='模糊查询阈值. 百分制. 默认值 80')

    parser.add_argument('-T', '--title', action='store_true', help='模糊查询标题')
    parser.add_argument('-t', '--tag', action='store_true', help='模糊查询标签')
    parser.add_argument('-u', '--username', action='store_true', help='模糊查询用户名')
    parser.add_argument('-C', '--caption', action='store_true', help='模糊查询描述')

    parser.add_argument(
        '-i', '--iid', action='store_true', help='查询插画 IID. 用 `,` 隔开多个')
    parser.add_argument(
        '-U', '--uid', action='store_true', help='查询用户 UID 的作品'
    )

    parser.add_argument(
        '-r', '--restricted', action='store_true', help='查询无效的插画'
    )
    parser.add_argument(
        '-a', '--all', action='store_true', help='显示所有'
    )

    return parser
ibd_query_parser = create_ibd_query_parser()


class WahuIllustDatabaseMethods:

    @classmethod
    @wahu_methodize()
    async def ibd_list(cls, ctx: WahuContext) -> list[str]:
        """列出所有数据库"""

        return list(ctx.ilst_bmdbs.keys())

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_list_bm(cls, ctx: WahuContext, name: str) -> list[IllustBookmark]:
        """列出所有收藏"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.all_bookmarks()

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_ilst_count(cls, ctx: WahuContext, name: str) -> int:
        """返回所有储存了的详情的数量"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            lst = ibd.all_illusts()

        return len(lst)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_set_bm(
        cls, ctx: WahuContext, name: str, iid: int, pages: list[int]
    ) -> tuple[bool, bool]:
        """设置收藏页"""

        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            if ctx.papi.logged_in:
                sink = ctx.papi.pool_illust_detail
            else:
                sink = None
                logger.warning('ibd_set_bm: PixivAPI 未登录，插画详情不会被添加到数据库')

            ret = await ibd.set_bookmark(
                iid, pages,
                get_detail=sink)
        return ret

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_ilst_detail(
        cls, ctx: WahuContext, name: str, iid: int
    ) -> Optional[IllustDetail]:
        """在数据库中查询插画详情"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.query_detail(iid)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_query_bm(
        cls, ctx: WahuContext, name: str, iid: int
    ) -> Optional[IllustBookmark]:
        """在数据库中查询收藏情况"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.query_bookmark(iid)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_fuzzy_query(
        cls,
        ctx: WahuContext,
        name: str,
        target: Literal['title', 'caption', 'tag', 'username'],
        keyword: str,
        cutoff: Optional[int]
    ) -> list[tuple[int, int]]:
        """
        数据库中模糊查询插画
        - `:return:` `list` of `(iid, score)`
        """

        if cutoff is None:
            cutoff = ctx.config.default_fuzzy_cutoff

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            match target:
                case 'title':
                    ret = ibd.query_title(keyword, cutoff=cutoff)

                case 'caption':
                    ret = ibd.query_caption(keyword, cutoff=cutoff)

                case 'tag':
                    ret = ibd.query_tag(keyword, cutoff=cutoff)

                case 'username':
                    ret = ibd.query_username(keyword, cutoff=cutoff)

                case _:
                    raise WahuRuntimeError(f'不合法的 target {target}')

        return [(iid, score) for iid, score in ret]

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_query_uid(
        cls, ctx: WahuContext, name: str, uid: int
    ) -> list[int]:
        """数据库中查询 `uid`"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.query_uid(uid)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_filter_restricted(cls, ctx: WahuContext, name: str) -> list[int]:
        """数据库中被作者删除的插画"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.filter_restricted()

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_query(
        cls, ctx: WahuContext, name: str, qs: str
    ) -> list[tuple[int, int]]:
        """使用命令行查询数据库"""

        args = click.parser.split_arg_string(qs)
        ns = ibd_query_parser.parse_args(args)

        if ns.iid:
            iids = list(map(int, ns.keyword.split(',')))

            iids_exist = []
            with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
                for iid in iids:
                    if ibd.query_bookmark(iid) is not None:
                        iids_exist.append(iid)

            return [(iid, -1) for iid in iids_exist]

        elif ns.uid:
            iids = await cls.ibd_query_uid(ctx, name, int(ns.keyword))
            return [(iid, -1) for iid in iids]

        elif ns.tag:
            return await cls.ibd_fuzzy_query(ctx, name, 'tag', ns.keyword, ns.cutoff)
        elif ns.username:
            return await cls.ibd_fuzzy_query(ctx, name, 'username', ns.keyword, ns.cutoff)
        elif ns.caption:
            return await cls.ibd_fuzzy_query(ctx, name, 'caption', ns.caption, ns.cutoff)

        elif ns.restricted:
            iids = await cls.ibd_filter_restricted(ctx, name)
            return [(iid, -1) for iid in iids]
        elif ns.all:
            with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
                return [(bm.iid, -1) for bm in ibd.all_bookmarks()]

        else:  # else if ns.title
            return await cls.ibd_fuzzy_query(ctx, name, 'title', ns.keyword, ns.cutoff)

    @classmethod
    @wahu_methodize()
    async def ibd_query_help(cls, ctx: WahuContext) -> str:
        """获得数据库查询命令的帮助"""

        return ibd_query_parser.format_help()

    @classmethod
    @wahu_methodize()
    async def ibd_new(
        cls, ctx: WahuContext, name: str
    ) -> None:
        """新增数据库"""

        if name in ctx.ilst_bmdbs.keys():
            raise WahuRuntimeError(f'插画数据库 {name} 已存在')

        new_ibd_ctx_wrapped: DatabaseContextManager[IllustBookmarkDatabase] = \
            DatabaseContextManager(IllustBookmarkDatabase(
                name, ctx.config.database_dir / f'{name}.db'
            ))
        ctx.ilst_bmdbs[name] = new_ibd_ctx_wrapped

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_remove(
        cls, ctx: WahuContext, name: str
    ) -> None:
        """删除数据库"""

        # 确保没有其他 task 在使用数据库
        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            ibd_path = ibd.db_path

        ctx.ilst_bmdbs.pop(name)

        if isinstance(ibd_path, str):
            ibd_path = Path(ibd_path)
        ibd_path.unlink()

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_copy(
        cls, ctx: WahuContext, name: str, target: str, iids: list[int]
    ) -> None:
        """复制数据库"""

        if target not in ctx.ilst_bmdbs.keys():
            raise WahuRuntimeError(f'目标数据库 {target} 不存在')

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:

            details = [ibd.query_detail(iid) for iid in iids]
            bms: list[IllustBookmark] = []
            for iid in iids:
                bm = ibd.query_bookmark(iid)
                if bm is None:
                    raise WahuRuntimeError(f'源数据库中不存在收藏 iid={iid}')
                else:
                    bms.append(bm)

        details = [dtl for dtl in details if dtl is not None]

        with await ctx.ilst_bmdbs[target](readonly=False) as target_ibd:

            [target_ibd.illusts_te.insert(details)]
            [target_ibd.bookmarks_te.insert(bms)]

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_export_json(
        cls, ctx: WahuContext, name: str
    ) -> str:
        """将数据库导出为 json"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            illusts = ibd.all_illusts()
            bookmarks = ibd.all_bookmarks()

        d = {'illusts': [dataclasses.asdict(ilst) for ilst in illusts],
             'bookmarks': [dataclasses.asdict(bm) for bm in bookmarks]}

        return json.dumps(d, ensure_ascii=False)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_import_json(
        cls, ctx: WahuContext, name: str, json_str: str
    ) -> None:
        """将 JSON 文件导入数据库"""

        d = json.loads(json_str)

        try:
            illusts: list[IllustDetail] = []

            for d_ilst in d['illusts']:
                d_ilst['user'] = PixivUserSummery(**d_ilst['user'])
                d_ilst['tags'] = [
                    IllustTag(n, t)
                    for n, t in d_ilst['tags']
                ]
                illusts.append(IllustDetail(**d_ilst))

            bookmarks = [IllustBookmark(**d_bm) for d_bm in d['bookmarks']]

        except TypeError or KeyError as e:
            raise WahuRuntimeError('不合法的 Export 文件') from e

        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            ibd.illusts_te.insert(illusts)
            ibd.bookmarks_te.insert(bookmarks)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_update(
        cls, ctx: WahuContext, name: str
    ) -> None:
        """更新数据库中的插画详情"""

        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            await ibd.update_detail(ctx.papi.pool_illust_detail)

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_get_config(
        cls, ctx: WahuContext, name: str
    ) -> IllustBookmarkingConfig:
        """获取数据库配置"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.config_table_editor.all()

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_set_config(
        cls, ctx: WahuContext, name: str, config: IllustBookmarkingConfig
    ) -> None:
        """设置数据库配置"""

        if isinstance(config, IllustBookmarkingConfig):
          cfg = config
        else:
          try:
              cfg = IllustBookmarkingConfig(
                  *(config[k] for k in IllustBookmarkingConfig.keys)
              )
          except KeyError as ke:
              raise WahuRuntimeError(f'缺少配置项 {ke.args}')

        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            ibd.config_table_editor.setall(cfg)


    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibd_update_subs(
        cls, ctx: WahuContext, name: str, page_num: Optional[int]
    ) -> AsyncGenerator[str, Optional[str]]:
        """更新数据库订阅"""

        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            coro_update, pipe = await ibd.update_subscrip(
                get_user_bookmarks=ctx.papi.user_bookmarks_illusts,
                get_user_illusts=ctx.papi.user_illusts,
                page_num=page_num
            )
        
        async def coro():
            with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
                await coro_update
        
        asyncio.create_task(coro())

        return pipe
