from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

from ibd_subscrip import mount as mount_ibd_subscrip

from wahu_backend.wahu_core.wahu_cli_helper import (dumps_dataclass,
                                                    print_help, wahu_cli_wrap)

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

    @ibd.command()
    @click.argument('name', type=str, required=True)
    @click.argument('iids', type=int, nargs=-1, required=True)
    @wahu_cli_wrap
    async def iid(
        cctx: click.Context,
        name: str,
        iids: list[int]
    ):
        """根据 IID 在数据库 NAME 中查询插画
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()

        if name not in wctx.ilst_bmdbs.keys():
            raise KeyError(f'数据库 {name} 不存在')

        with await wctx.ilst_bmdbs[name](readonly=True) as ibd:
            for iid in iids:
                dtl = ibd.query_detail(iid)

                if dtl is None:
                    pipe.putline(f'{iid} 未找到')
                else:
                    pipe.putline(dumps_dataclass(dtl))

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
        wctx, pipe, wmethods = obj.unpkg()

        bm = await wmethods.ibd_query_bm.f(wmethods, wctx, name, iid)

        if bm is None:
            pipe.putline(f'未找到 {iid}')
        else:
            pipe.putline(str(bm.pages))


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
        wctx, pipe, wmethods = obj.unpkg()

        await wmethods.ibd_set_bm.f(wmethods, wctx, name, iid, pages)
