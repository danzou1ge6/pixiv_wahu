import asyncio
from functools import partial
import inspect
import traceback
from typing import TYPE_CHECKING, Any, Coroutine, Type
import click


if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj, WahuContext

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap
from wahu_backend.wahu_methods import WahuMethods


NAME = '执行 Python 命令'
DESCRIPTION = '创建一个 Python 名称空间，并在其中执行脚本'


_HELP = '''使用名称 wctx 可以访问当前的 WahuContext 实例
使用名称 wm 可以使用所有 WahuMethod ， WahuContext 已被绑定

print(__o: object) 取代了内置的 print() 方法，该方法不换行
println(__o: object) 将再打印一个换行符

使用 coro_asign(coro: Corotine, name: str) 可将 coro 的返回值赋给名称为 name 的变量
也可直接输入一个 Corotine ，将打印其返回值

输入 exit 退出. 如果未使用 --preserve-namespace, -p 选项，名称空间不会被保存
如果使用了 -p 选项，退出后再次使用 -p 可以重新访问此名称空间

支持多行输入: 「:」或「\\」结尾的行将启动多行输入模式
'''

_NAMESPACE = {}

def _cleanup_namespace(cctx: click.Context, param: click.Parameter, value: Any):
    global _NAMESPACE
    if value:
        _NAMESPACE = {}


class WahuMethodsWithContextBound:
    def __init__(self, wctx: 'WahuContext'):
        self.wctx = wctx
    def __getattr__(self, name: str):
        return partial(getattr(WahuMethods, name), self.wctx)


def mount(wexe: click.Group):

    @wexe.command()
    @click.option(
        '--cleanup-namespace', '-c', is_flag=True, callback=_cleanup_namespace,
        expose_value=False, is_eager=True,
        help='清除全局名称空间'
        )
    @click.option('--preserve-namespace', '-p', is_flag=True, help='使用全局名称空间')
    @wahu_cli_wrap
    async def py(cctx: click.Context, preserve_namespace: bool):
        """执行 Python 命令

        如果使用了 --preserve-namespace ，将使用一个模块级的全局变量来保存名称空间
        使用 --cleanup-namespace 将清空上述的名称空间
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        def _println(s: object):
            pipe.putline(str(s))

        def _print(s: object):
            pipe.put(text=str(s))

        def _coro_asign(ns: dict[str, Any], coro: Coroutine, name: str):
            tsk = asyncio.create_task(coro)
            def cbk(_tsk: asyncio.Task):
                ns[name] = _tsk.result()
            tsk.add_done_callback(cbk)

        namespace = {
            'wctx': wctx,
            'wm': WahuMethodsWithContextBound(wctx),
            'println': _println,
            'print': _print
        }
        namespace['coro_asign'] = partial(_coro_asign, namespace)

        pipe.putline('输入 help 来获得帮助')

        if preserve_namespace:
            global _NAMESPACE
            pipe.putline('使用全局名称空间')
            _NAMESPACE.update(namespace)
            namespace = _NAMESPACE


        while True:
            cmd = await pipe.get(prefix='>>>')

            if cmd == 'exit':
                break

            if cmd == 'help':
                pipe.putline(_HELP)

            if cmd.endswith(':') or cmd.endswith('\\'):
                if cmd.endswith('\\'):
                    cmd = cmd[:-1]
                while True:
                    ln = await pipe.get(prefix='>>:')

                    if ln == '':
                        break

                    cmd += '\n' + ln

            try:
                # 首先尝试 eval 模式
                ret = eval(cmd, namespace)

                if inspect.iscoroutine(ret):
                    pipe.putline(str(await ret))
                else:
                    pipe.putline(str(ret))

            except SyntaxError:
                # 然后尝试 exec 模式
                try:
                    exec(cmd, namespace)
                except Exception:
                    pipe.putline(traceback.format_exc())

            except Exception:
                pipe.putline(traceback.format_exc())



