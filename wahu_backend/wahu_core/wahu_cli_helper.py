import asyncio
import dataclasses
import functools
import json
import traceback
from typing import TYPE_CHECKING, Any, Callable, Concatenate, Coroutine, ParamSpec, TypeVar

import click

if TYPE_CHECKING:
    from .wahu_cli import CliClickCtxObj


def print_help(cctx: click.Context, param: click.Parameter, value: Any):
    """助手函数 用以覆盖 click 打印到终端"""

    obj: CliClickCtxObj = cctx.obj

    if not value or cctx.resilient_parsing:
        return
    obj.pipe.put(cctx.get_help())
    obj.pipe.close()

T = TypeVar('T')
P = ParamSpec('P')


def wahu_cli_wrap(f: Callable[Concatenate[click.Context, P], Coroutine[None, None, None]]):

    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    @click.pass_context
    @functools.wraps(f)
    def g(cctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> None:

        obj: CliClickCtxObj = cctx.obj

        async def h() -> None:
            try:
                await f(cctx, *args, **kwargs)
            except Exception:
                obj.pipe.put(traceback.format_exc())
            finally:
                obj.pipe.close()

        asyncio.create_task(h())

    return g


def dumps_dataclass(dc: object) -> str:
    return json.dumps(
        dataclasses.asdict(dc),
        indent=2,
        ensure_ascii=False
    )
