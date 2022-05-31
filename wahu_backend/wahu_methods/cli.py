from dataclasses import dataclass
from pathlib import Path
import traceback
from typing import Any, AsyncGenerator, Type

from ..wahu_core import CliIOPipe, WahuContext, wahu_methodize
from .illust_database import WahuIllustDatabaseMethods
from .illust_repo import IllustRepoMethods
from .misc import WahuMiscMethods
from .pixiv import WahuPixivMethods
from .wahu_generator import WahuGeneratorMethods


class CliClickCtxObj:
    """挂载到 `click.Context.obj` ，来传入必要的上下文信息"""

    def __init__(
        self,
        wctx: WahuContext,
        pipe: CliIOPipe
    ):
        self.wctx = wctx
        self.pipe = pipe

        self.d: dict[str, Any]


@dataclass
class CliScriptInfo:
    path: Path
    name: str
    descrip: str
    code: str


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

        pipe = CliIOPipe()
        cctx_obj = CliClickCtxObj(ctx, pipe)

        try:
            ret_code = ctx.wexe(
                grouped_cmd,
                obj=cctx_obj,
                standalone_mode=False,
                prog_name=''
            )

            if ret_code != None:
                pipe.put('命令解析出错. 使用 --help 查看命令语法')
                pipe.close()

        except Exception:
            pipe.put(traceback.format_exc())
            pipe.close()

        return pipe

    @classmethod
    @wahu_methodize()
    async def cli_reload(cls, ctx: WahuContext) -> None:
        """重新从 `config.cli_script_dir` 加载命令行脚本"""

        ctx.load_cli_scripts(reload=True)

    @classmethod
    @wahu_methodize()
    async def cli_list(cls, ctx: WahuContext) -> list[CliScriptInfo]:
        """返回命令行脚本的信息"""

        return [CliScriptInfo(
            cs.path, cs.name, cs.descrip, cs.code
        ) for cs in ctx.cli_scripts]
