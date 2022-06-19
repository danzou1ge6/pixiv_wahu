from typing import TYPE_CHECKING, Optional, Literal

import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import less, wahu_cli_wrap, print_help

from helpers import table_factory

NAME = '池状态'
DESCRIPTION = '插画缓存池、图片缓存池、生成器缓存池状态'


def mount(wexe: click.Group):

    @wexe.group()
    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    def pool():
        """管理缓存池"""
        pass

    @pool.command()
    @click.option(
        '--verbose', '-v', type=click.Choice(['ilst', 'img', 'gen']),
        help='打印所有键'
    )
    @wahu_cli_wrap
    async def status(
        cctx: click.Context, verbose: Optional[Literal['ilst', 'img', 'gen']]
    ):
        """打印缓存池的状态

        ilst for 插画; img for 图片; gen for 生成器.
        """

        obj: CliClickCtxObj = cctx.obj
        wctx = obj.wctx

        if verbose is None:

            tbl = table_factory()
            tbl.add_rows([
                ('插画缓存池',
                f'{len(wctx.papi.ilst_pool)} / {wctx.papi.ilst_pool_size}',
                f'{len(wctx.papi.ilst_pool) * 100 / wctx.papi.ilst_pool_size:.3f}%'),
                ('图片缓存池',
                f'{len(wctx.image_pool.pool)} / {wctx.image_pool.size}',
                f'{len(wctx.image_pool.pool) * 100 / wctx.image_pool.size:.3f}%'),
                ('生成器缓存池',
                f'{len(wctx.agenerator_pool.pool)} / {wctx.agenerator_pool.size}',
                f'{len(wctx.agenerator_pool.pool) * 100 / wctx.agenerator_pool.size:.3f}%')
            ])

            obj.pipe.putline(tbl.get_string())

        else:
            if verbose == 'ilst':
                keys = [str(k) for k in wctx.papi.ilst_pool.keys()]
            elif verbose == 'img':
                keys = list(wctx.image_pool.pool.keys())
            elif verbose == 'gen':
                keys = list(wctx.agenerator_pool.pool.keys())

            await less('\n'.join(keys), obj.pipe)

    @pool.command()
    @click.argument('name', type=click.Choice(['img', 'ilst', 'gen']))
    @wahu_cli_wrap
    async def clean(cctx: click.Context, name: Literal['ilst', 'img', 'gen']):
        """清空缓存池"""

        obj: CliClickCtxObj = cctx.obj
        wctx = obj.wctx

        if name == 'ilst':
            wctx.papi.ilst_pool.clear()
        elif name == 'img':
            wctx.image_pool.pool.clear()
        elif name == 'gen':
            wctx.agenerator_pool.pool.clear()

