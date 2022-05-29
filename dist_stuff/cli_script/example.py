from typing import TYPE_CHECKING
import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import WahuContext
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

"""
一个示例命令行脚本，使用 click 创建
click 文档详见 https://click.palletsprojects.com/en/8.1.x/
更多实例参见 `wahu_cli/*`
"""


NAME = 'echo'  # 命令的名称
DESCRIPTION = '示例命令行脚本'  # 命令的描述

def init_hook(ctx: 'WahuContext'):
    """当此脚本被加载时执行；可选"""

    ctx._msg_from_script_echo = 'wuhu, take off !'  # type: ignore

def cleanup_hook(ctx: 'WahuContext'):
    """当应用退出时执行；可选"""
    pass

def mount(wexe: click.Group, wahu_cli_wrap):
    """
    将自定义的命令挂载到 `wexe` ，即命令行处理的根命令
    装饰器 `wahu_cli_wrap` 用于完成以下工作
    - 将异步回调函数转换为同步函数，通过 `asyncio.create_task`
    - 将回调函数中发生的异常捕获，输出到 IO 管道
    - 在回调函数退出后，关闭 IO 管道
    - 注册 `--help` 选项，这样可以通过 `<命令名> --help` 获得帮助信息
    """

    @wexe.command()
    @click.argument('echo', type=str)  # 添加一个位置参数 `echo` ，更多用法详见 click 文档
    @wahu_cli_wrap
    # 下面的这个称之为「回调函数」
    async def echo(cctx: click.Context, echo: str):
        """回声

        打印 ECHO ，然后从命令行读取三次输入并打印
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()
        # wctx: WahuContext 实例，详见 `wahu_backend/wahu_core/wahu_context.py`
        # pipe: 命令行 IO 管道 CliIOPipe 实例，详见 `wahu_backend/wahu_core/wahu_cli.py`
        # wmethods: WahuMethodsCollection 子类，内含所有 WahuMethods ，
        # 详见 `wahu_backend/wahu_methods/*`

        # 打印一行字符
        pipe.putline(f'message from script echo: {wctx._msg_from_script_echo}')  # type: ignore
        pipe.putline('start echoing')
        pipe.putline(echo)

        for i in range(3):
            pipe.putline('输入一些东西')
            # 读取输入
            inp = await pipe.get()
            pipe.putline(f'{i}: {inp}')

        pipe.putline('echo finished')



