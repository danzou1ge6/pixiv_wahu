from secrets import choice
from typing import TYPE_CHECKING, Optional
import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import WahuContext
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_helper import wahu_cli_wrap
from wahu_backend.constants import illustDbImageURL
from wahu_backend.wahu_methods import WahuMethods

from wahu_cli.helpers import format_bookmarked_illust_detail


"""
一个示例命令行脚本，使用 click 创建
click 文档详见 https://click.palletsprojects.com/en/8.1.x/
更多实例参见 `wahu_cli/*`
"""


NAME = '示例'  # 命令的名称
DESCRIPTION = '示例命令行脚本'  # 命令的描述

def init_hook(ctx: 'WahuContext'):
    """当此脚本被加载时执行；可选"""

    ctx._msg_from_script_echo = 'wuhu, take off !'  # type: ignore

def cleanup_hook(ctx: 'WahuContext'):
    """当应用退出时执行；可选"""
    pass

def mount(wexe: click.Group):
    """
    将自定义的命令挂载到 `wexe` ，即命令行处理的根命令
    """

    @wexe.command()
    @click.argument('echo', type=str)  # 添加一个位置参数 `echo` ，更多用法详见 click 文档
    # 装饰器 `wahu_cli_wrap` 用于完成以下工作
    # - 将异步回调函数转换为同步函数，通过 `asyncio.create_task`
    # - 将回调函数中发生的异常捕获，输出到 IO 管道
    # - 在回调函数退出后，关闭 IO 管道
    # - 注册 `--help` 选项，这样可以通过 `<命令名> --help` 获得帮助信息
    @wahu_cli_wrap
    # 下面的这个称之为「回调函数」
    async def echo(cctx: click.Context, echo: str):
        """回声

        打印 ECHO ，然后从命令行读取三次输入并打印
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe
        # wctx: WahuContext 实例，详见 `wahu_backend/wahu_core/wahu_context.py`
        # pipe: 命令行 IO 管道 CliIOPipe 实例，详见 `wahu_backend/wahu_core/wahu_cli.py`
        # wmethods: WahuMethodsCollection 子类，内含所有 WahuMethods ，
        # 详见 `wahu_backend/wahu_methods/*`

        # 打印一行字符
        pipe.putline(f'message from script echo: {wctx._msg_from_script_echo}')  # type: ignore
        pipe.put('start echoing: ')
        pipe.putline(echo)

        for i in range(3):
            pipe.putline('输入一些东西')
            # 读取输入
            inp = await pipe.get()
            pipe.putline(f'{i}: {inp}')

        pipe.putline('echo finished')


    @wexe.command()
    @click.argument('name', type=str, required=False)
    @wahu_cli_wrap
    async def random_img(cctx: click.Context, name: Optional[str]):
        """随机打印一张数据库 NAME 中的插画

        如果未提供 NAME ，则随机选择一个数据库
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe = obj.wctx, obj.pipe

        if name is None:
            name = choice(list(wctx.ilst_bmdbs.keys()))

        if name not in wctx.ilst_bmdbs.keys():
            raise RuntimeError(f'fatal: 数据库 {name} 不存在')

        with await wctx.ilst_bmdbs[name](readonly=True) as ibd:  # type: ignore
            bm = choice(ibd.all_bookmarks())

            dtl = ibd.query_detail(bm.iid)
            if dtl is not None:
                pipe.put(
                    f'[:img={illustDbImageURL}/{name}/{bm.iid}/{choice(bm.pages)}]'
                    f'{format_bookmarked_illust_detail(dtl, bm)}'
                )
            else:
                pipe.put(f'[:img={illustDbImageURL}/{name}/{bm.iid}/{choice(bm.pages)}]')


