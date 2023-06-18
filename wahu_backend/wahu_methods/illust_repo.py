import asyncio
import itertools
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar, Type

from ..aiopixivpy import IllustDetail
from ..file_tracing import FileEntry, FileTracer
from ..illust_bookmarking import IllustBookmark
from ..sqlite_tools.database_ctx_man import DatabaseContextManager
from ..wahu_core import (GenericWahuMethod, WahuArguments, WahuContext,
                         wahu_methodize)
from ..wahu_core.core_exceptions import WahuRuntimeError
from ..wahu_core.repo_db_link import RepoEntry
from .lib_logger import logger

if TYPE_CHECKING:
    from . import WahuMethods
    from ..file_tracing.ft_datastructure import FileEntryRaw

# ------------------------------------------------------------------- 中间件
RT = TypeVar('RT')

async def _check_repo_name(
    m: GenericWahuMethod[RT],
    cls: Type['WahuMethods'],
    args: WahuArguments,
    ctx: WahuContext
) -> RT:
    """检查储存库名的中间件"""

    if 'name' not in args.keys():
        raise WahuRuntimeError(f'_check_repo_name: 缺少参数 name')

    if args.name not in ctx.ilst_repos.keys():
        raise WahuRuntimeError(f'_check_repo_name: 储存库名 {args.name} 不在上下文中')

    return await m(cls, args, ctx)


# ------------------------------------------------------------------- 数据模型
@dataclass(slots=True)
class FileEntryWithURL(FileEntry):
    url: str

    def __hash__(self) -> int:
        return hash(self.fid)

    def __eq__(self, __o: 'FileEntryRaw') -> bool:
        return self.fid == __o.fid

@dataclass(slots=True)
class RepoSyncAddReport:
    db_name: str
    entries: list[FileEntryWithURL]

# ------------------------------------------------------------------- 工具
INVALID_CHAR_CVT = [
    ('?', '？'), ( '/', '-'), ( '\\', '、'), ( ',', '：'),
    ('*', '^'), ( '"', "'"), ( '<', '《'), ( '>', '》'), ( '|', '+')
]

def _cvt_invalid_path_char(s: str):
    for frm, t in INVALID_CHAR_CVT:
        s = s.replace(frm, t)
    return s


# ------------------------------------------------------------------- 方法
class IllustRepoMethods:

    @classmethod
    @wahu_methodize()
    async def ir_new(
        cls, ctx: WahuContext, name: str, prefix: str
    ) -> None:
        """新增储存库"""
        if name in ctx.ilst_repos.keys():
            raise WahuRuntimeError(f'储存库 {name} 已存在')

        new_repo = DatabaseContextManager[FileTracer](
            FileTracer(name, ctx.config.wpath(prefix))
        )

        ctx.ilst_repos[name] = new_repo

        ctx.repo_db_link.repos[name] = RepoEntry(
            ctx.config.wpath(prefix), name, []
        )
        ctx.repo_db_link.write()

    @classmethod
    @wahu_methodize()
    async def ir_list(cls, ctx: WahuContext) -> list[str]:
        """列出储存库"""

        return list(ctx.ilst_repos.keys())

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_linked_db(
        cls, ctx: WahuContext, name: str
    ) -> list[str]:
        """列出连接的数据库"""

        return ctx.repo_db_link.repos[name].linked_databases

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_set_linked_db(
        cls, ctx: WahuContext, name: str, db_names: list[str]
    ) -> None:
        """
        设置连接的数据库，数据库可以不存在
        """
        for dbn in db_names:
            if dbn not in ctx.ilst_bmdbs.keys():
                logger.warn(f'ir_set_linked_db: 数据库 {dbn} 不存在')

        ctx.repo_db_link.set_repo_linked_db(name, db_names)

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_calc_sync(
        cls, ctx: WahuContext, name: str
    ) -> tuple[list[FileEntry], list[RepoSyncAddReport]]:
        """
        计算更新储存库要删除的条目和要添加的条目
        - `:return:` ([ 要删除的, ... ], [( 来源的数据库名, 要新增的 ), ...])
        所有路径均为相对路径
        """

        db_file_entries: list[tuple[str, set[FileEntryWithURL]]] = []

        for ibd_ctxman in ctx.repo_db_link.dfr(name):
            with await ibd_ctxman(readonly=True) as ibd:

                bms = ibd.all_bookmarks()

                # 获取详情：首先从数据库，如果没有则从 PixivAPI
                async def get_detail(iid: int) -> IllustDetail:
                    dtl = ibd.query_detail(iid)

                    if dtl is not None:
                        return dtl

                    dtl = await ctx.papi.pool_illust_detail(iid)

                    # 顺便加入数据库
                    ibd.illusts_te.insert([dtl])

                    return dtl

                async def get_file_entries(bm: IllustBookmark) -> list[FileEntryWithURL]:
                    dtl = await get_detail(bm.iid)
                    ext = dtl.image_origin[0].split('.')[-1]
                    return [
                        FileEntryWithURL(
                            # 此处的路径不包括储存库根目录
                            Path(
                                _cvt_invalid_path_char(  # 去除 Windows 无法作为路径的字符
                                    ctx.config.file_name_template.format(
                                    dtl, i) + f'.{ext}'
                                )
                            ),
                            fid,
                            dtl.image_origin[i]
                        )
                        for i, fid in enumerate(bm.as_fids())
                    ]

                file_entrie_list: list[list[FileEntryWithURL]] = await asyncio.gather(
                    *(get_file_entries(bm) for bm in bms)
                )

                # 压平
                file_entries: set[FileEntryWithURL] = set(
                    itertools.chain(*file_entrie_list)
                )

                db_file_entries.append((ibd.name, file_entries))

        with await ctx.ilst_repos[name](readonly=True) as ft:
            ft_file_entries = set(ft.all_index())

        to_add_db_file_entries: list[RepoSyncAddReport] = [
            RepoSyncAddReport(db_name, list(file_entries.difference(ft_file_entries)))
            for db_name, file_entries in db_file_entries
        ]

        to_del_file_entries = list(
            ft_file_entries.difference(
                reduce(
                    lambda x, y: x.union(y),
                    (file_entry for _, file_entry in db_file_entries)
                )
            )
        )

        return (to_del_file_entries, to_add_db_file_entries)

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_add_cache(
        cls, ctx: WahuContext, name: str, file_entries: list[FileEntry]
    ) -> None:
        """将条目添加到 cached"""

        # 去重
        file_entries = list(set(file_entries))

        with await ctx.ilst_repos[name](readonly=False) as ft:
            ft.add_cache(file_entries)

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_download(
        cls, ctx: WahuContext, name: str, file_entries_withurl: list[FileEntryWithURL]
    ) -> None:
        """下载到储存库. 路径为相对路径"""

        root_path = ctx.ilst_repos[name].dd.root_path

        async def dl_coro(fewu: FileEntryWithURL):
            file_path = root_path / fewu.path
            if not file_path.exists():

                image = await ctx.image_pool.get_image(fewu.url, descript=str(fewu.path))
                with open(file_path, 'wb') as wf:
                    wf.write(image)
            else:
                logger.warn(f'ir_download: 文件 {file_path} 已存在，不再下载')

        [asyncio.create_task(dl_coro(fewu)) for fewu in file_entries_withurl]

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_update_index(
        cls, ctx: WahuContext, name: str
    ) -> list[FileEntry]:
        """检查本地文件，将 cached 中下载完成的移入 indexed"""

        with await ctx.ilst_repos[name](readonly=False) as ft:
            return ft.update_index()

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_rm_index(
        cls, ctx: WahuContext, name: str, index_fids: list[str]
    ) -> None:
        """从 indexed 删除"""

        with await ctx.ilst_repos[name](readonly=False) as ft:
            ft.remove_index(index_fids)


    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_validate(
        cls, ctx: WahuContext, name: str
    ) -> tuple[list[FileEntry], list[Path]]:
        """校验文件和索引是否有效. 路径为绝对路径"""

        with await ctx.ilst_repos[name](readonly=True) as ft:
            return (
                ft.validate_index(),
                ft.validate_files()
            )

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_remove_file(
        cls, ctx: WahuContext, name: str, files: list[Path]
    ) -> None:
        """删除储存库内的文件"""

        root_path = ctx.ilst_repos[name].dd.root_path

        for p in files:
            if p.parent != root_path:
                raise WahuRuntimeError(f'请求删除的文件 {str(p)} 不在储存库目录下')
            p.unlink()

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_get_cache(
        cls, ctx: WahuContext, name: str
    ) -> list[FileEntry]:
        """获取 cached 表"""

        with await ctx.ilst_repos[name](readonly=True) as ft:
            return ft.all_cache()

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_get_index(
        cls, ctx: WahuContext, name: str
    ) -> list[FileEntry]:
        """获取 indexed 表"""

        with await ctx.ilst_repos[name](readonly=True) as ft:
            return ft.all_index()

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_empty_cache(
        cls, ctx: WahuContext, name: str
    ) -> None:
        """清除 cached 表"""

        with await ctx.ilst_repos[name](readonly=False) as ft:
            ft.empty_cache()

    @classmethod
    @wahu_methodize(middlewares=[_check_repo_name])
    async def ir_remove(cls, ctx: WahuContext, name: str) -> None:
        """移除储存库"""

        ctx.ilst_repos.pop(name)
        ctx.repo_db_link.repos.pop(name)
        ctx.repo_db_link.update_rfd()
        ctx.repo_db_link.write()
