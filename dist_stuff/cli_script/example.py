import random
from secrets import choice
from typing import TYPE_CHECKING, Optional
import click

if TYPE_CHECKING:
    from wahu_backend.wahu_core import WahuContext
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap, print_help, less
from wahu_backend.constants import illustDbImageURL
from wahu_backend.wahu_methods import WahuMethods

from wahu_cli.helpers import format_bookmarked_illust_detail, table_factory
from wahu_cli.print_wahu import _WAHU


"""
一个示例命令行脚本，使用 click 创建
click 文档详见 https://click.palletsprojects.com/en/8.1.x/
更多实例参见 `wahu_cli/*` (可执行档包中此目录在 `Lib/site-packages/wahu_cli`)
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
    将自定义的命令挂载到 `wexe` ，即命令行处理的根命令。
    在命令行中不需要输入 `wexe`
    """

    @wexe.group()
    # 将 example 命令作为 wexe 的子命令
    @click.option('--help', is_flag=True, callback=print_help,
                  expose_value=False, is_eager=True)
    def example():
        """示例命令行脚本"""

    @example.command()
    # 将下面定义的命令作为 example 命令的子命令
    @click.argument('echo', type=str)  # 添加一个位置参数 `echo` ，更多用法详见 click 文档
    # 装饰器 `wahu_cli_wrap` 用于完成以下工作
    # - 将异步回调函数转换为同步函数，通过 `asyncio.create_task`
    # - 将回调函数中发生的异常捕获，输出到 IO 管道
    # - 在回调函数退出后，关闭 IO 管道
    # - 注册 `--help` 选项，这样可以通过 `<命令名> --help` 获得帮助信息
    @wahu_cli_wrap
    # 下面的这个称之为「回调函数」
    # 在命令行中执行 example echo ECHO 来调用此回调函数
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

        # 打印一行字符，以换行符开头，在 web 终端中这会导致新建一个 <pre> 标签
        pipe.putline(f'message from script echo: {wctx._msg_from_script_echo}')  # type: ignore
        pipe.putline('start echoing: ')
        # 打印但是不以换行符开头，这会追加到上一个 <pre> 标签的末尾
        pipe.put(echo)

        for i in range(3):
            pipe.putline('输入一些东西')
            # 读取输入
            # prefix 参数会改变提示符
            inp = await pipe.get(prefix='...')
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
                # 并排打印图片和 <text>
                pipe.put(
                    src=f'{illustDbImageURL}/{name}/{bm.iid}/{choice(bm.pages)}',
                    # format_bookmarked_illust_detail 是一个格式化插画详情的助手函数
                    text=format_bookmarked_illust_detail(dtl, bm)
                )
            else:
                # 打印一张 src=<url> 的图片
                pipe.put(f'[:img={illustDbImageURL}/{name}/{bm.iid}/{choice(bm.pages)}]')

    @example.command()
    @wahu_cli_wrap
    async def long_text(cctx: click.Context):
        """使用 less 打印很长一段文本"""

        pipe = cctx.obj.pipe

        pipe.putline('接下来会打印六十行随机生成的字符')

        txt = []
        for _ in range(70):
            txt.append(
                ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789 ,.', k=30))
            )

        # 每次回车打印下一段
        await less(
            '\n'.join(txt),
            cctx.obj.pipe,
            lines_per_page=20)

    @example.command()
    @wahu_cli_wrap
    async def rewrite_last(cctx: click.Context):
        """使用 rewrite 覆盖上一次 putline

        less 就是通过 rewrite 实现的
        """

        pipe = cctx.obj.pipe

        pipe.putline(_WAHU)

        # echo=False 导致输入后的回显立即被 [:erase] 删除
        # 这行等价于：
        # await pipe.get('回车来覆盖上一段字符')
        # await pipe.put(erase=True)
        await pipe.get(prefix='回车来覆盖上一段字符', echo=False)

        pipe.put(text='Wahu!', rewrite=True)

    @example.command()
    @wahu_cli_wrap
    async def list_cli(cctx: click.Context):
        """
        列出所有命令行脚本
        """

        cli_list = await WahuMethods.cli_list(cctx.obj.wctx)

        # table_factory 会返回一个新建的 PrettyTable ，使用命令行输出 Style
        # 其默认 header=False
        tbl = table_factory()

        # 打开 header ，并设置 field_names
        tbl.header = True
        tbl.field_names = ['名', '描述', '文件名']

        tbl.add_rows([(csi.name, csi.descrip, csi.path.name) for csi in cli_list])

        cctx.obj.pipe.putline(tbl.get_string())

