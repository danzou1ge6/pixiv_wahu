from typing import TYPE_CHECKING
import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_helper import (dumps_dataclass,
                                                    print_help, wahu_cli_wrap)
from wahu_backend.constants import illustDbImageURL
from wahu_backend.wahu_methods import WahuMethods

from ibd_subscrip import mount as mount_ibd_subscrip
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

    mount_ibd_subscrip(ibd)
    mount_ibd_count(ibd)

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
                        pipe.put(f'[:img={src}]')
                        pipe.putline(text)
                    else:
                        pipe.put(f'[:img={src}]{text}')
                else:
                    pipe.putline(f'[:img={src}]')


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
    @click.argument('pages', type=int, nargs=-1, required=True)
    @wahu_cli_wrap
    async def set_bm(
        cctx: click.Context,
        name: str,
        iid: int,
        pages: list[int]
    ):
        """将数据库 NAME 中的插画 IID 的收藏页码设置为 PAGES
        """

        obj: 'CliClickCtxObj' = cctx.obj

        await WahuMethods.ibd_set_bm(obj.wctx, name, iid, pages)
