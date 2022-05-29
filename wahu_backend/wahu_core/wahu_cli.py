import asyncio
import functools
import importlib
from importlib import resources
import sys
import traceback
from asyncio import Event
from inspect import Traceback
from pathlib import Path
from queue import Queue
from typing import (Any, AsyncGenerator, Callable, Concatenate, Coroutine,
                    Optional, ParamSpec, TypeVar)

import click

from .core_exceptions import WahuCliScriptError

TP = str

class CliIOPipe(AsyncGenerator[TP, TP]):
    """使用异步生成器接口的命令行 IO 管道"""

    def __init__(self, max_size: int = -1):
        self.output_queue: Queue[TP] = Queue(maxsize=max_size)
        self.input_queue: Queue[TP] = Queue(maxsize=max_size)
        self.output_event = Event()
        self.input_event = Event()

    def put(self, val: TP):
        """输出"""

        self.output_queue.put(val)
        self.output_event.set()

    def putline(self, val: TP):
        self.put(val + '\n')

    async def __anext__(self) -> TP:
        """
        前端读取一条输出，如果队列中没有则等待；
        如果管道关闭，抛出 `StopAsyncIteration`
        """


        await self.output_event.wait()

        val = self.output_queue.get()

        if val == '[:close]':
            raise StopAsyncIteration

        if self.output_queue.empty():
            self.output_event.clear()

        return val

    async def asend(self, val: TP | None) -> TP:
        """
        前端输入，然后读取一条输出；
        如果输入 `None` ，则不进行输入；
        如果输入 `[:stop]` ，则设置 `stopped_event` ，取消 task
        """


        if val is not None:
            self.input_queue.put(val)
            self.input_event.set()

        return await self.__anext__()

    async def get(self) -> TP:
        """等待前端输入"""

        self.put('[:input]')

        await self.input_event.wait()

        val = self.input_queue.get()

        if self.input_queue.empty():
            self.input_event.clear()

        return val

    async def athrow(
        self,
        excpt_vale: Exception,
        excpt_type: Optional[type] = None,
        excpt_tcbk: Optional[Traceback] = None
    ):
        """在生成器中引起一条异常"""
        raise excpt_vale

    async def aclose(self):
        """设置管道关闭"""
        self.put('[:close]')

    def close(self):
        self.put('[:close]')



def print_help(cctx: click.Context, param: click.Parameter, value: Any):
    """助手函数 用以覆盖 click 打印到终端"""

    if not value or cctx.resilient_parsing:
        return
    cctx.obj.pipe.put(cctx.get_help())
    cctx.obj.pipe.close()
    cctx.exit()

T = TypeVar('T')
P = ParamSpec('P')


def wahu_cli_wrap(f: Callable[Concatenate[click.Context, P], Coroutine[None, None, None]]):

    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    @click.pass_context
    @functools.wraps(f)
    def g(cctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> None:

        async def h() -> None:
            try:
                await f(cctx, *args, **kwargs)
            except Exception:
                cctx.obj.pipe.put(traceback.format_exc())
            finally:
                cctx.obj.pipe.close()

        asyncio.create_task(h())

    return g


class WahuCliScript:
    """储存命令行脚本信息"""

    def __init__(
        self,
        path: Path,
        name: str,
        descrip: str,
        code: str,
        init_hook: Callable[[Any], None] | None,
        cleanup_hook: Callable[[Any], None] | None
    ):
        self.path = path
        self.name = name
        self.descrip = descrip
        self.code = code
        self.init_hook = init_hook
        self.cleanup_hook = cleanup_hook


def _load_cli_scripts_from_dir(
    script_dir: Path, wexe: click.Group, reload: bool=False
) ->list[WahuCliScript]:

    cli_scripts = []

    sys.path.append(str(script_dir))

    for item in script_dir.iterdir():
        if item.suffix == '.py':

            m = importlib.import_module(item.stem)
            if reload:
                importlib.reload(m)

            try:
                name = m.NAME
                description = m.DESCRIPTION
            except AttributeError:
                raise WahuCliScriptError('缺少元信息 name, description')

            try:
                init_hook = m.init_hook
            except AttributeError:
                init_hook = None

            try:
                cleanup_hook = m.cleanup_hook
            except AttributeError:
                cleanup_hook = None

            try:
                mount = m.mount
            except AttributeError:
                raise WahuCliScriptError('缺少 mount')

            mount(wexe, wahu_cli_wrap)

            with open(item, 'r', encoding='utf-8') as rf:
                code = rf.read()

            cli_scripts.append(WahuCliScript(
                item,
                name,
                description,
                code,
                init_hook,
                cleanup_hook
            ))

    sys.path.remove(str(script_dir))

    return cli_scripts

def load_cli_scripts(script_dir: Path, reload: bool=False
) -> tuple[list[WahuCliScript], click.Group]:
    """
    加载所有命令行脚本
    - :param script_dir: 脚本所在的目录
    - :param reload: 是否重新加载命令行脚本的模块
    - :return: `wexe`: `click.Group`, `cli_scripts`
    """

    cli_scripts = []

    @click.group()
    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    @click.pass_context
    @staticmethod
    def wexe(cctx: click.Context):
        pass

    # 从 wahu_cli 包中加载
    try:
        cli_pkg_path = resources.path('wahu_cli', 'reload_cli.py').__enter__().parent
        cli_scripts += _load_cli_scripts_from_dir(cli_pkg_path, wexe, reload=reload)
    except ModuleNotFoundError:
        pass

    cli_scripts += _load_cli_scripts_from_dir(script_dir, wexe, reload=reload)

    return cli_scripts, wexe



