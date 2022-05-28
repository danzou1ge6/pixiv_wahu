import asyncio
import functools
from typing import Any, AsyncGenerator, Callable, Coroutine, ParamSpec, Type, TypeVar

import click

from ..wahu_core import CliIOPipe, WahuContext, wahu_methodize
from .illust_database import WahuIllustDatabaseMethods
from .illust_repo import IllustRepoMethods
from .misc import WahuMiscMethods
from .pixiv import WahuPixivMethods
from .wahu_generator import WahuGeneratorMethods


class CliClickCtxObj:

    def __init__(
        self,
        wctx: WahuContext,
        pipe: CliIOPipe,
        wmethods: Type['WahuMetdodsWithCli']
    ):
        self.wctx = wctx
        self.pipe = pipe
        self.wmethods = wmethods


@click.group()
@click.pass_context
def wexe(cctx: click.Context):
    pass

T = TypeVar('T')
P = ParamSpec('P')

def coro_as_task(f: Callable[P, Coroutine[None, None, None]]):
    @functools.wraps(f)
    def g(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.create_task(f(*args, **kwargs))
    return g


class WahuMetdodsWithCli(
    WahuIllustDatabaseMethods, WahuPixivMethods, WahuGeneratorMethods,
    IllustRepoMethods, WahuMiscMethods):

    @classmethod
    @wahu_methodize()
    async def wahu_exec(cls, ctx: WahuContext, cmd: str) -> AsyncGenerator[str, str]:
        """启动一个命令行的执行"""

        # 分组命令行
        splitted_with_quote = cmd.split('"')
        grouped_cmd = []
        for i, block in enumerate(splitted_with_quote):
            if i % 2 == 0:
                grouped_cmd += block.split(' ')
            else:
                grouped_cmd.append(block)
        grouped_cmd = [g for g in grouped_cmd if g != '']

        pipe = CliIOPipe[str]()
        cctx_obj = CliClickCtxObj(ctx, pipe, cls)

        wexe(grouped_cmd, obj=cctx_obj, standalone_mode=False)

        return pipe
