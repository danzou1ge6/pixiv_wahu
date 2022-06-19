import asyncio
import itertools
from typing import TYPE_CHECKING, Coroutine

import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from helpers import table_factory, report_dl_coro

from wahu_backend.wahu_core.wahu_cli_util import print_help, wahu_cli_wrap, less
from wahu_backend.wahu_methods import WahuMethods
from wahu_backend.pixiv_image.image_getter import PixivImageGetError

NAME = '插画储存库操作'
DESCRIPTION = '一些对插画储存库的操作'


async def ignore_dl_error(coro: Coroutine[None, None, None]) -> None:
    try:
        await coro
    except PixivImageGetError as pige:
        pass


def mount(wexe: click.Group):

    @wexe.group()
    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    def ir():
        """一些对插画储存库的操作"""
        pass


    @ir.command()
    @click.option('--verbose', '-v', is_flag=True, help='打印连接的数据库')
    @wahu_cli_wrap
    async def ls(cctx: click.Context, verbose: bool):
        """打印插画储存库列表

        不存在的数据库前将用 ! 标识
        """

        obj: CliClickCtxObj = cctx.obj

        if verbose:
            tbl = table_factory()

            for r in obj.wctx.repo_db_link.repos.values():

                dbs = []
                for dbn in r.linked_databases:
                    if dbn not in obj.wctx.ilst_bmdbs.keys():
                        dbs.append('!' + dbn)
                    else:
                        dbs.append(dbn)

                tbl.add_row((r.name, ', '.join(dbs)))

            text = tbl.get_string()

        else:
            text = ' '.join(obj.wctx.ilst_repos.keys())

        obj.pipe.putline(text)


    @ir.command()
    @click.argument('name', type=str, required=True)
    @click.argument(
        'prefix',
        type=click.Path(exists=False, file_okay=False, writable=True),
        required=True
    )
    @wahu_cli_wrap
    async def new(cctx: click.Context, name: str, prefix: str):
        """创建插画储存库 NAME 在 PREFIX
        """

        obj: CliClickCtxObj = cctx.obj

        await WahuMethods.ir_new(obj.wctx, name, prefix)


    @ir.command()
    @click.argument('name', type=str, required=True)
    @wahu_cli_wrap
    async def rm(cctx: click.Context, name: str):
        """删除插画储存库 NAME
        """

        obj: CliClickCtxObj = cctx.obj

        if not name in obj.wctx.ilst_repos.keys():
            raise KeyError(f'fatal: 储存库 {name} 不存在')

        await WahuMethods.ir_remove(obj.wctx, name)


    @ir.command()
    @click.argument('name', type=str, required=True)
    @click.argument('ibd_names', type=str, nargs=-1, required=True)
    @wahu_cli_wrap
    async def set_ibd(cctx: click.Context, name: str, ibd_names: tuple[str]):
        """设置储存库 NAME 连接的数据库为 IBD_NAMES
        """

        await WahuMethods.ir_set_linked_db(cctx.obj.wctx, name, list(ibd_names))

    @ir.command()
    @click.argument('name', type=str, required=True)
    @click.option('--no-less', '-n', is_flag=True, help='不使用 less')
    @wahu_cli_wrap
    async def sync(cctx: click.Context, name: str, no_less: bool):
        """同步储存库 NAME
        """

        obj: CliClickCtxObj = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        to_del, to_add_reports = await WahuMethods.ir_calc_sync(wctx, name)

        del_tbl = table_factory()
        del_tbl.header = True
        del_tbl.field_names = ['FID',  '文件']
        del_tbl.add_rows([(fe.fid, fe.path) for fe in to_del])

        add_tbl = table_factory()
        add_tbl.header = True
        add_tbl.field_names = ['FID', '数据库', '文件']
        for rpt in to_add_reports:
            add_tbl.add_rows([(fe.fid, rpt.db_name, fe.path) for fe in rpt.entries])

        sync_report_text = '删除:\n' + del_tbl.get_string() + '\n'
        sync_report_text += '新增:\n' + add_tbl.get_string()

        if no_less:
            pipe.putline(sync_report_text)
        else:
            await less(sync_report_text, pipe)

        if await pipe.get(prefix='继续[y/*]?', echo=False) != 'y':
            return

        await WahuMethods.ir_rm_index(wctx, name, [fe.fid for fe in to_del])

        await WahuMethods.ir_add_cache(
            wctx, name,
            list(itertools.chain(*(rpt.entries for rpt in to_add_reports)))
        )

        to_dl_fileentries = list(itertools.chain(
            *(rpt.entries for rpt in to_add_reports)
        ))

        prefix = wctx.ilst_repos[name].dd.root_path

        path_list = [prefix / fe.path for fe in to_dl_fileentries]
        url_list = [fe.url for fe in to_dl_fileentries]

        coro_list = [
            ignore_dl_error(WahuMethods.download_image(wctx, url, pth))
            for url, pth in zip(url_list, path_list)
        ]

        dl_tsk = asyncio.gather(*coro_list)

        rpt_dl_tsk = asyncio.create_task(report_dl_coro(path_list, wctx, pipe))

        await dl_tsk

        await asyncio.sleep(0.5)  # 等待下载完成结果刷新
        rpt_dl_tsk.cancel()

        new_entries = await WahuMethods.ir_update_index(wctx, name)

        if len(new_entries) < len(path_list):
            pipe.putline('警告: 新增索引数小于下载数，部分文件可能下载失败')

    @ir.command()
    @click.argument('name', type=str, required=True)
    @wahu_cli_wrap
    async def update(cctx: click.Context, name: str):
        """更新储存库 NAME 的索引
        """

        await WahuMethods.ir_update_index(cctx.obj.wctx, name)


    @ir.command()
    @click.argument('name', type=str, required=True)
    @click.option('--no-less', '-n', is_flag=True, help='不使用 less')
    @wahu_cli_wrap
    async def clean(cctx: click.Context, name: str, no_less: bool):
        """清理储存库 NAME 的索引和文件
        """

        obj: CliClickCtxObj = cctx.obj
        pipe, wctx = obj.pipe, obj.wctx

        invalid_entries, invalid_paths = await WahuMethods.ir_validate(wctx, name)

        invalid_etr_tbl = table_factory()
        invalid_etr_tbl.field_names = ['FID', '路径']
        invalid_etr_tbl.header = True
        invalid_etr_tbl.add_rows([
            (fe.fid, str(fe.path)) for fe in invalid_entries
        ])

        text = '无效索引:\n' + invalid_etr_tbl.get_string()
        text += '\n无效文件\n' + '\n'.join((str(p) for p in invalid_paths))

        if no_less:
            pipe.putline(text)
        else:
            await less(text, pipe)

        if await pipe.get('继续[y/*]?', echo=False) != 'y':
            return

        await WahuMethods.ir_rm_index(wctx, name, [fe.fid for fe in invalid_entries])
        await WahuMethods.ir_remove_file(wctx, name, invalid_paths)

