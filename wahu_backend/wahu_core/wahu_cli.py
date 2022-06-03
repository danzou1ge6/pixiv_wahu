import importlib
import platform
import shutil
import sys
from asyncio import Event
from importlib import resources
from inspect import Traceback
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Optional
from wcwidth import wcswidth

import click

from .core_exceptions import WahuCliScriptError
from .wahu_cli_helper import print_help

if TYPE_CHECKING:
    from .wahu_context import WahuContext


class CliIoPipeABC:

    def put(
        self,
        text: Optional[str]=None,
        src: Optional[str]=None,
        rewrite: bool=False,
        erase: bool=False
    ) -> None:
        raise NotImplemented

    def putline(self, val: str) -> None:
        raise NotImplemented

    async def get(self, prefix: Optional[str]=None, echo: bool=True) -> str:
        raise NotImplemented


class CliIOPipe(CliIoPipeABC, AsyncGenerator[str, str]):
    """使用异步生成器接口的命令行 IO 管道"""

    def __init__(self, max_size: int = -1):
        self.oustrut_queue: Queue[str] = Queue(maxsize=max_size)
        self.input_queue: Queue[str] = Queue(maxsize=max_size)
        self.oustrut_event = Event()
        self.input_event = Event()

    def _oustrut(self, val: str) -> None:
        """输出"""

        self.oustrut_queue.put(val)
        self.oustrut_event.set()

    def put(
        self,
        text: Optional[str]=None,
        src: Optional[str]=None,
        rewrite: bool=False,
        erase: bool=False
    ):
        """
        在终端打印

        - 如果 erase 为真，则清除上一块打印
        - 如果 rewrite 为真，则使用 text 覆盖上一块 <pre>
        - 如果提供了 src 和 text ，并排打印
        - 如果提供了 src ，打印图片
        - 如果提供了 text ，直接打印文本；若 text 以 '\n' 开头，则新建一块 <pre>
        """

        if erase:
            self._oustrut('[:erase]')
            return

        if rewrite:
            if text is None:
                raise RuntimeError('rewrite 需要提供 text')
            else:
                self._oustrut('[:rewrite]' + text)
                return

        if src is not None:
            if text is None:
                self._oustrut(f'[:img={src}]')
            else:
                self._oustrut(f'[:img={src}]{text}')
            return

        if text is not None:
            self._oustrut(text)
            return

        raise RuntimeError('至少传入 text')


    def putline(self, val: str) -> None:
        """新建一块 <pre> 打印文本"""

        self.put(text='\n' + val)

    async def __anext__(self) -> str:
        """
        前端读取一条输出，如果队列中没有则等待；
        如果管道关闭，抛出 `StopAsyncIteration`
        """


        await self.oustrut_event.wait()

        val = self.oustrut_queue.get()

        if val == '[:close]':
            raise StopAsyncIteration

        if self.oustrut_queue.empty():
            self.oustrut_event.clear()

        return val

    async def asend(self, val: str | None) -> str:
        """
        前端输入，然后读取一条输出；
        如果输入 `None` ，则不进行输入；
        如果输入 `[:stop]` ，则设置 `stopped_event` ，取消 task
        """


        if val is not None:
            self.input_queue.put(val)
            self.input_event.set()

        return await self.__anext__()

    async def get(self, prefix: str='>', echo=True) -> str:
        """等待前端输入"""

        self.put(f'[:input={prefix}]')

        await self.input_event.wait()

        val = self.input_queue.get()

        if not echo:
            self.put('[:erase]')

        if self.input_queue.empty():
            self.input_event.clear()

        return val

    async def athrow(
        self,
        excpt_vale: Exception,
        excpt_type: Optional[type] = None,
        excpt_tcbk: Optional[Traceback] = None
    ) -> None:
        """在生成器中引起一条异常"""
        raise excpt_vale

    async def aclose(self) -> None:
        """设置管道关闭"""
        self.put('[:close]')

    def close(self) -> None:
        self.put('[:close]')


class CliIOPipeTerm(CliIoPipeABC):
    """输出到终端的命令行 IO 管道"""

    def __init__(self):
        self.close_event = Event()

        self.last_block_count: int = 0

        if platform.system() == 'Windows':
            from ctypes import windll
            k = windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)

    def _back_rows(self, n: int) -> None:
        print('\r', end='')
        print(f'\x1b[{n}A', end='')

    @property
    def term_width(self) -> int:
        return shutil.get_terminal_size()[0]

    def _calc_displayed_line_count(self, s: str) -> int:
        return sum(
            (int(wcswidth(line) / self.term_width) + 1 for line in s.split('\n'))
        )

    def _output(self, text: str) -> None:

        if text.startswith('\n'):
            text = text[1:]
        displayed_line_count = self._calc_displayed_line_count(text)

        if text.startswith('\n'):
            self.last_block_count = displayed_line_count
            print('')
        else:
            self.last_block_count += displayed_line_count

        print(text, end='')

    def _clean_lines(self, n: int) -> None:
        self._back_rows(n - 1)
        term_width = self.term_width
        for _ in range(n):
            print(''.join((' ' for _ in range(term_width))))
        self._back_rows(n)

    def put(
        self,
        text: Optional[str]=None,
        src: Optional[str]=None,
        rewrite: bool=False,
        erase: bool=False
    ) -> None:

        if erase or rewrite:
            self._clean_lines(self.last_block_count)
            self.last_block_count = 0
            if erase:
                return

        if src is not None:
            if text is None:
                self._output(f'[:img={src}]')
            else:
                self._output(f'[:img={src}]\n{text}')
            return

        if text is not None:
            self._output(text)

    def putline(self, val: str) -> None:

        self.put(text='\n' + val)

    async def get(self, prefix: str='>', echo=True) -> str:

        click.echo('\n' + prefix + ' ', nl=False)
        val = input()

        if not echo:
            self._clean_lines(self._calc_displayed_line_count(val))
            self._back_rows(1)

        return val

    def close(self) -> None:
        self.close_event.set()


class CliClickCtxObj:
    """挂载到 `click.Context.obj` ，来传入必要的上下文信息"""

    def __init__(
        self,
        wctx: 'WahuContext',
        pipe: CliIOPipe | CliIOPipeTerm
    ):
        self.wctx = wctx
        self.pipe = pipe

        self.d: dict[str, Any]



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

    sys.path.insert(0, str(script_dir))

    for item in script_dir.iterdir():
        if item.suffix == '.py':

            m = importlib.import_module(item.stem)
            if reload:
                importlib.reload(m)

            if hasattr(m, 'IGNORE') and m.IGNORE:
                continue

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

            mount(wexe)

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



