import dataclasses
import json
from pathlib import Path
from typing import Literal, Optional, TypeVar

from wahu_backend.aiopixivpy.datastructure_illust import IllustTag

from ..aiopixivpy import IllustDetail, PixivUserSummery
from ..illust_bookmarking import IllustBookmark, IllustBookmarkDatabase
from ..illust_bookmarking.ib_datastructure import IllustBookmarkingConfig
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from ..wahu_core import (GenericWahuMethod, WahuArguments, WahuContext,
                         wahu_methodize)
from ..wahu_core.core_exceptions import WahuRuntimeError
from .logger import logger

RT = TypeVar('RT')  # Return Type


async def _check_db_name(
    m: GenericWahuMethod[RT], args: WahuArguments, ctx: WahuContext
) -> RT:
    """检查数据库名的中间件"""

    if 'name' not in args:
        raise WahuRuntimeError(f'_check_db_name：未提供数据库名')

    if args.name not in ctx.ilst_bmdbs.keys():
        raise WahuRuntimeError(f'_check_db_name: 数据库名 {args.name} 不在上下文中')

    return await m(args, ctx)


class WahuIllustDatabaseMethods:

    @wahu_methodize()
    @staticmethod
    async def ibd_list(ctx: WahuContext) -> list[str]:
        """列出所有数据库"""

        return list(ctx.ilst_bmdbs.keys())

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_list_bm(ctx: WahuContext, name: str) -> list[IllustBookmark]:
        """列出所有收藏"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.all_bookmarks()

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_set_bm(
        ctx: WahuContext, name: str, iid: int, pages: list[int]
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

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_ilst_detail(
        ctx: WahuContext, name: str, iid: int
    ) -> Optional[IllustDetail]:
        """在数据库中查询插画详情"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.query_detail(iid)

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_query_bm(
        ctx: WahuContext, name: str, iid: int
    ) -> Optional[IllustBookmark]:
        """在数据库中查询收藏情况"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.query_bookmark(iid)

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_fuzzy_query(
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

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_query_uid(
        ctx: WahuContext, name: str, uid: int
    ) -> list[int]:
        """数据库中查询 `uid`"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.query_uid(uid)

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_filter_restricted(ctx: WahuContext, name: str) -> list[int]:
        """数据库中被作者删除的插画"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.filter_restricted()

    @wahu_methodize()
    @staticmethod
    async def ibd_new(
        ctx: WahuContext, name: str
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

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_remove(
        ctx: WahuContext, name: str
    ) -> None:
        """删除数据库"""

        # 确保没有其他 task 在使用数据库
        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            ibd_path = ibd.db_path

        ctx.ilst_bmdbs.pop(name)

        if isinstance(ibd_path, str):
            ibd_path = Path(ibd_path)
        ibd_path.unlink()

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_copy(
        ctx: WahuContext, name: str, target: str, iids: list[int]
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

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_get_config(
        ctx: WahuContext, name: str
    ) -> IllustBookmarkingConfig:
        """获取数据库配置"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            return ibd.config_table_editor.all()

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_set_config(
        ctx: WahuContext, name: str, config: IllustBookmarkingConfig
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


    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_update_subs(
        ctx: WahuContext, name: str, page_num: Optional[int]
    ) -> int:
        """更新数据库订阅"""

        with await ctx.ilst_bmdbs[name](readonly=False) as ibd:
            return len(await ibd.update_subscrip(
                get_user_bookmarks=ctx.papi.user_bookmarks_illusts,
                get_user_illusts=ctx.papi.user_illusts,
                page_num=page_num
            ))

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_export_json(
        ctx: WahuContext, name: str
    ) -> str:
        """将数据库导出为 json"""

        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:
            illusts = ibd.all_illusts()
            bookmarks = ibd.all_bookmarks()

        d = {'illusts': [dataclasses.asdict(ilst) for ilst in illusts],
             'bookmarks': [dataclasses.asdict(bm) for bm in bookmarks]}

        return json.dumps(d, ensure_ascii=False)

    @wahu_methodize(middlewares=[_check_db_name])
    @staticmethod
    async def ibd_import_json(
        ctx: WahuContext, name: str, json_str: str
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



