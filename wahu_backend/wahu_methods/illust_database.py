import dataclasses
import json
from pathlib import Path
from typing import Literal, Optional, Type, TypeVar

from ..aiopixivpy import IllustDetail, PixivUserSummery, IllustTag
from ..illust_bookmarking import IllustBookmark, IllustBookmarkDatabase
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from ..wahu_core import (GenericWahuMethod, WahuArguments, WahuContext,
                         wahu_methodize, WahuMethodsCollection)
from ..wahu_core.core_exceptions import WahuRuntimeError
from .logger import logger

RT = TypeVar('RT')  # Return Type


async def _check_db_name(
    m: GenericWahuMethod[RT],
    cls: Type[WahuMethodsCollection],
    args: WahuArguments,
    ctx: WahuContext
) -> RT:
    """检查数据库名的中间件"""

    if 'name' not in args:
        raise WahuRuntimeError(f'_check_db_name：未提供数据库名')

    if args.name not in ctx.ilst_bmdbs.keys():
        raise WahuRuntimeError(f'_check_db_name: 数据库名 {args.name} 不在上下文中')

    return await m(cls, args, ctx)


class WahuIllustDatabaseMethods(WahuMethodsCollection):

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
    @wahu_methodize()
    async def ibd_new(
        cls, ctx: WahuContext, name: str
    ) -> bool:
        """新增数据库"""

        if name in ctx.ilst_bmdbs.keys():
            return False

        new_ibd_ctx_wrapped: DatabaseContextManager[IllustBookmarkDatabase] = \
            DatabaseContextManager(IllustBookmarkDatabase(
                name, ctx.config.database_dir / f'{name}.db'
            ))
        ctx.ilst_bmdbs[name] = new_ibd_ctx_wrapped

        return True

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



