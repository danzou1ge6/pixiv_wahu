import dataclasses
import json
from typing import TYPE_CHECKING, Literal

import click

from wahu_backend.wahu_methods import WahuMethods

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import (dumps_dataclass,
                                                    print_help, wahu_cli_wrap)
from wahu_backend.constants import serverImageURL

from helpers import format_illust_detail

NAME = 'Pixiv 操作'
DESCRIPTION = '一些对 Pixiv 的操作'


def mount(wexe: click.Group):

    @wexe.group()
    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    def pixiv():
        """一些对 Pixiv 数据库的操作"""
        pass

    @pixiv.command()
    @click.argument('iid', type=int, required=True)
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
    @click.option(
        '--size', '-s',
        type=click.Choice(['original', 'large', 'medium', 'square_mdium']),
        default='large'
    )
    @wahu_cli_wrap
    async def iid(
        cctx: click.Context,
        iid: int,
        verbose: bool,
        image: int,
        page: int,
        size: Literal['original', 'large', 'medium', 'square_mdium']
    ):
        """在 Pixiv 上查询插画 IID 的详情和图片"""

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        dtl = await WahuMethods.p_ilst_detail(wctx, iid)

        if verbose:
            text = dumps_dataclass(dtl)
        else:
            text = format_illust_detail(dtl)

        if page >= dtl.page_count:
            raise RuntimeError(f'fatal: 插画 {iid} 只有 {dtl.page_count} 页')

        match size:
            case 'original':
                image_url = dtl.image_origin[page]
            case 'medium':
                image_url = dtl.image_medium[page]
            case 'large':
                image_url = dtl.image_large[page]
            case 'square_medium':
                image_url = dtl.image_sqmedium[page]


        if image == 0:
            pipe.putline(text)
        elif image == 1:
            if verbose:
                pipe.put(src=f'{serverImageURL}/{image_url}')  # type: ignore
                pipe.putline(text)
            else:
                pipe.put(src=f'{serverImageURL}/{image_url}', text=text)  # type: ignore
        else:
            pipe.put(src=f'{serverImageURL}/{image_url}')  # type: ignore


    @pixiv.command()
    @click.argument('iids', type=int, nargs=-1, required=True)
    @wahu_cli_wrap
    async def add_bm(
        cctx: click.Context, iids: list[int]
    ):
        """收藏插画 IID 到 Pixiv 账号"""

        obj: 'CliClickCtxObj' = cctx.obj

        await WahuMethods.p_ilstbm_add(obj.wctx, iids)

    @pixiv.command()
    @click.argument('iids', type=int, nargs=-1, required=True)
    @wahu_cli_wrap
    async def del_bm(
        cctx: click.Context, iids: list[int]
    ):
        """删除插画 IID 从 Pixiv 账号"""

        obj: 'CliClickCtxObj' = cctx.obj

        await WahuMethods.p_ilstbm_rm(obj.wctx, iids)


