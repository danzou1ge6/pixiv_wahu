import asyncio
import dataclasses
import functools
import itertools
import json
import shutil
import traceback
from typing import (TYPE_CHECKING, Any, Callable, Concatenate, Coroutine, Optional,
                    ParamSpec, TypeVar)
from wcwidth import wcswidth

import click

if TYPE_CHECKING:
    from .wahu_cli import CliClickCtxObj, CliIoPipeABC

"""
WahuCli 的低级助手函数
"""


def print_help(cctx: click.Context, param: click.Parameter, value: Any):
    """助手函数 用以覆盖 click 打印到终端"""

    obj: CliClickCtxObj = cctx.obj

    if not value or cctx.resilient_parsing:
        return
    obj.pipe.putline(cctx.get_help())
    obj.pipe.close()
    cctx.exit(-1)

T = TypeVar('T')
P = ParamSpec('P')


def wahu_cli_wrap(f: Callable[Concatenate[click.Context, P], Coroutine[None, None, None]]):

    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True, help='打印帮助信息')
    @click.pass_context
    @functools.wraps(f)
    def g(cctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> None:

        obj: CliClickCtxObj = cctx.obj

        async def h() -> None:
            try:
                await f(cctx, *args, **kwargs)
            except Exception:
                obj.pipe.putline(traceback.format_exc())
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


def _group_str(s: str,  group_size: int) -> list[str]:

    length = int(wcswidth(s) / group_size) + 1

    groups = [
        s[group_size * i : group_size * ( i + 1)]
        for i in range(length - 1)
    ]
    groups.append(s[group_size * (length - 1):])

    return groups


async def less(
    s: str,
    pipe: 'CliIoPipeABC',
    lines_per_page: int=20
) -> None:
    """分页打印

    回车 下一页
    u 上一页
    u<n> 上 n 页，超出 [0, page_num] 区间会被截断
    d<n> 下 n 页，超出范围会被截断
    g<n> 到第 n 页，超出范围会被截断
    当当前页为 page_num 时，退出分页
    """

    if hasattr(pipe, 'term_size'):
        # 如果 pipe 是 `CliIoPipeTerm` ，则使用其标识的终端尺寸
        term_width, term_height = pipe.term_size  # type: ignore

        lines: list[str] = list(itertools.chain(
            *(_group_str(ln, term_width) for ln in s.split('\n'))
        ))
        lines_per_page = term_height - 2

    else:
        # 否则认为是 WebUI ，不考虑终端尺寸
        lines = s.split('\n')

    page_num = int(len(lines) / lines_per_page) + 1

    pages = ['\n'.join(lines[lines_per_page*i:lines_per_page*(i+1)])
             for i in range(page_num - 1)]
    pages.append('\n'.join(lines[lines_per_page*(page_num - 1):]))

    pipe.putline('\n')

    pointer = 0

    while pointer < page_num:

        text = pages[pointer]
        text += f'\nLESS --- {pointer} of {page_num} ---'
        pipe.put(text=text, rewrite=True)

        cmd = await pipe.get(prefix='Less >', echo=False)

        try:
            if cmd == 'u':
                pointer -= 1
            elif cmd == '':
                pointer += 1
            elif cmd.startswith('u'):
                pointer -= int(cmd[1:])
            elif cmd.startswith('d'):
                pointer += int(cmd[1:])
            elif cmd.startswith('g'):
                pointer = int(cmd[1:])
        except ValueError:
            pass

        if pointer < 0:
            pointer = 0
        elif pointer > page_num:
            pointer = page_num
