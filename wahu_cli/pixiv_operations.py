import dataclasses
import json
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_helper import (dumps_dataclass,
                                                    print_help, wahu_cli_wrap)

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
    @wahu_cli_wrap
    async def iid(
        cctx: click.Context, iid: int
    ):
        """在 Pixiv 上查询插画 IID 的详情"""

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()

        dtl = await wmethods.p_ilst_detail.f(wmethods, wctx, iid)

        pipe.putline(dumps_dataclass(dtl))

    @pixiv.command()
    @click.argument('iids', type=int, nargs=-1, required=True)
    @wahu_cli_wrap
    async def add_bm(
        cctx: click.Context, iids: list[int]
    ):
        """收藏插画 IID 到 Pixiv 账号"""

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()

        await wmethods.p_ilstbm_add.f(wmethods, wctx, iids)

    @pixiv.command()
    @click.argument('iids', type=int, nargs=-1, required=True)
    @wahu_cli_wrap
    async def del_bm(
        cctx: click.Context, iids: list[int]
    ):
        """删除插画 IID 从 Pixiv 账号"""

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()

        await wmethods.p_ilstbm_rm.f(wmethods, wctx, iids)


