import itertools
from typing import TYPE_CHECKING, Optional
import click

from wahu_cli.helpers import table_factory

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj, WahuContext

from wahu_backend.wahu_core.wahu_cli_util import (dumps_dataclass,
                                                    print_help, wahu_cli_wrap)
from wahu_backend.constants import illustDbImageURL
from wahu_backend.wahu_methods import WahuMethods

from ibd_count import mount as mount_ibd_count
from helpers import format_bookmarked_illust_detail


NAME = '插画数据库操作'
DESCRIPTION = '一些对插画数据库的操作'


def mount(wexe: click.Group):

    @wexe.group()
    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    def ibd():
        """一些对插画数据库的操作"""
        pass

    mount_ibd_count(ibd)

    @ibd.command()
    @click.option('--verbose', '-v', is_flag=True, help='打印连接的数据库')
    @wahu_cli_wrap
    async def ls(cctx: click.Context, verbose: bool):
        """打印插画数据库列表
        """

        obj: CliClickCtxObj = cctx.obj

        if verbose:
            obj.wctx.repo_db_link.update_rfd()

            tbl = table_factory()

            for dbn in obj.wctx.ilst_bmdbs.keys():
                if dbn in obj.wctx.repo_db_link.rname_for_db.keys():
                    repos = obj.wctx.repo_db_link.rname_for_db[dbn]
                else:
                    repos = []

                tbl.add_row((dbn, ', '.join(repos)))

            text = tbl.get_string()

        else:
            text = ' '.join(obj.wctx.ilst_bmdbs.keys())

        obj.pipe.putline(text)

    @ibd.command()
    @click.argument('name', type=str, required=True)
    @wahu_cli_wrap
    async def new(cctx: click.Context, name: str):
        """创建一个新的插画数据库 NAME
        """

        await WahuMethods.ibd_new(cctx.obj.wctx, name)

        # 创建文件
        wctx: 'WahuContext' = cctx.obj.wctx
        with await wctx.ilst_bmdbs[name](readonly=False) as ibd:
            pass


    @ibd.command()
    @click.argument('name', type=str, required=True)
    @wahu_cli_wrap
    async def rm(cctx: click.Context, name: str):
        """删除插画数据库 NAME
        """

        obj: CliClickCtxObj = cctx.obj

        if name not in obj.wctx.ilst_bmdbs.keys():
            raise KeyError(f'fatal: 数据库 {name} 不存在')

        await WahuMethods.ibd_remove(obj.wctx, name)

    @ibd.command()
    @click.argument('name', type=str, required=True)
    @click.argument('iids', type=int, nargs=-1, required=True)
    @click.option(
        '--verbose', '-v', is_flag=True,
        help='是否打印详情中所有信息'
    )
    @click.option(
        '--image', '-i', count=True,
        help='输入一次则打印图片，输入两次则不打印详情'
    )
    @click.option(
        '--page', '-p', type=int, default=0,
        help='打印图片的页码'
    )
    @wahu_cli_wrap
    async def iid(
        cctx: click.Context,
        name: str,
        iids: list[int],
        verbose: bool,
        image: int,
        page: int
    ):
        """根据 IID 在数据库 NAME 中查询插画
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        if name not in wctx.ilst_bmdbs.keys():
            raise KeyError(f'fatal: 数据库 {name} 不存在')

        with await wctx.ilst_bmdbs[name](readonly=True) as ibd:
            for iid in iids:
                dtl = ibd.query_detail(iid)
                bm = ibd.query_bookmark(iid)

                if bm is None:
                    pipe.putline(f'{iid} 未找到收藏')
                    return

                if dtl is None:
                    pipe.putline(f'警告: {iid} 未找到详情')
                    text = ''
                    image = 2

                else:

                    if verbose:
                        text = dumps_dataclass(dtl)
                    else:
                        text = format_bookmarked_illust_detail(dtl, bm)

                    if page >= dtl.page_count:
                        pipe.putline(f'警告: 插画 {iid} 只有 {dtl.page_count} 页')
                        image = 0

                src = f'{illustDbImageURL}/{name}/{iid}/{page}'

                if image == 0:
                    pipe.putline(text)
                elif image == 1:
                    if verbose:
                        pipe.put(src=src)
                        pipe.putline(text)
                    else:
                        pipe.put(src=src, text=text)
                else:
                    pipe.put(src=src)


    @ibd.command()
    @click.argument('name', type=str, required=True)
    @click.argument('iid', type=int, required=True)
    @wahu_cli_wrap
    async def bm(
        cctx: click.Context,
        name: str,
        iid: int
    ):
        """打印数据库 NAME 中插画 IID 的收藏页码
        """

        obj: 'CliClickCtxObj' = cctx.obj

        bm = await WahuMethods.ibd_query_bm(obj.wctx, name, iid)

        if bm is None:
            obj.pipe.putline(f'未找到 {iid}')
        else:
            obj.pipe.putline(str(bm.pages))


    @ibd.command()
    @click.argument('name', type=str, required=True)
    @click.argument('iid', type=int, required=True)
    @click.argument('pages', type=int, nargs=-1, required=False)
    @click.option('--delete', '-d', is_flag=True)
    @wahu_cli_wrap
    async def set_bm(
        cctx: click.Context,
        name: str,
        iid: int,
        pages: list[int],
        delete: bool
    ):
        """将数据库 NAME 中的插画 IID 的收藏页码设置为 PAGES
        """

        obj: 'CliClickCtxObj' = cctx.obj

        if delete:
            pages = []
        else:
            if pages == []:
                raise RuntimeError('需要参数 pages 或者指明 -d')

        await WahuMethods.ibd_set_bm(obj.wctx, name, iid, pages)

    @ibd.command()
    @click.argument('name', type=str, required=True)
    @click.option(
        '--server-url', '-s', type=str, default='https://i.pximg.net',
        help='设置图片服务器，默认为 https://i.pximg.net')
    @click.option(
        '--output', '-o', type=click.Path(dir_okay=False, writable=True, exists=False),
        required=False,
        help='指定输出文件，若未指出则打印'
    )
    @wahu_cli_wrap
    async def export_imgurl(
        cctx: click.Context,
        name: str,
        server_url: str,
        output: Optional[str]
    ):
        """导出数据库中所有插画的图片 URL

        只能导出已下载详情的的
        """

        obj: 'CliClickCtxObj' = cctx.obj

        if name not in obj.wctx.ilst_bmdbs.keys():
            raise KeyError(f'fatal: 数据库 {name} 不存在')

        with await obj.wctx.ilst_bmdbs[name](readonly=True) as ibd:
            illusts = ibd.all_illusts()

        urls = itertools.chain(
            *([f'{server_url}{url}' for url in ilst.image_origin]
              for ilst in illusts)
        )

        if output is None:
            obj.pipe.putline('\n'.join(urls))
        else:
            with open(obj.wctx.config.wpath(output), 'w', encoding='utf-8') as wf:
                wf.write('\n'.join(urls))

    @ibd.command()
    @click.argument('name', type=str, required=True)
    @wahu_cli_wrap
    async def update(cctx: click.Context, name: str):
        """更新数据库 NAME 中的详情
        """

        obj: 'CliClickCtxObj' = cctx.obj

        num = await WahuMethods.ibd_update(obj.wctx, name)

        obj.pipe.putline(f'更新了 {num} 条插画详情')
