from dataclasses import dataclass
from pathlib import Path
import traceback
from typing import AsyncGenerator, Optional
import webbrowser
from click.parser import split_arg_string


from ..wahu_core.wahu_cli import CliIOPipeTerm, CliIoPipeABC
from ..wahu_core.core_exceptions import WahuRuntimeError
from ..wahu_core import CliIOPipe, WahuContext, wahu_methodize, CliClickCtxObj
from .illust_database import WahuIllustDatabaseMethods
from .illust_repo import IllustRepoMethods
from .misc import WahuMiscMethods
from .pixiv import WahuPixivMethods
from .wahu_generator import WahuGeneratorMethods
from .get_token import WahuGetTokenMethods
from .tag_statistic import WahuTagStatisticMethods
from .log import WahuLoggingMethods


@dataclass(slots=True)
class CliScriptInfo:
    path: Path
    name: str
    descrip: str
    code: str


def _wahu_exec_with_pipe(
    ctx: WahuContext, args: list[str], pipe: CliIoPipeABC, in_terminal: bool
) -> None:

    cctx_obj = CliClickCtxObj(ctx, pipe, in_terminal)

    try:
        ret_code = ctx.wexe.main(
            args,
            obj=cctx_obj,
            standalone_mode=False,
            prog_name=''
        )

        if ret_code is not None and ret_code != -1:
            pipe.putline('命令解析出错. 使用 --help 查看命令语法')
            pipe.close()

    except Exception:
        pipe.putline(traceback.format_exc())
        pipe.close()


class WahuMetdodsWithCli(
    WahuIllustDatabaseMethods, WahuPixivMethods, WahuGeneratorMethods,
    IllustRepoMethods, WahuMiscMethods, WahuGetTokenMethods,
    WahuTagStatisticMethods, WahuLoggingMethods
):

    @classmethod
    @wahu_methodize()
    async def wahu_exec(
        cls, ctx: WahuContext, cmd: str
    ) -> AsyncGenerator[str, Optional[str]]:
        """启动一个命令行的执行 (WebUI)"""

        pipe = CliIOPipe()

        _wahu_exec_with_pipe(
            ctx,
            split_arg_string(cmd),
            pipe,
            False
        )

        return pipe

    @classmethod
    @wahu_methodize()
    async def wahu_client_exec(
        cls, ctx: WahuContext, args: list[str], term_size: tuple[int, int]
    ) -> AsyncGenerator[str, Optional[str]]:
        """启动一个命令行的执行 (TermCLI)"""

        pipe = CliIOPipeTerm(term_size)

        _wahu_exec_with_pipe(ctx, args, pipe, True)

        return pipe


    @classmethod
    @wahu_methodize()
    async def wahu_cli_complete(cls, ctx: WahuContext, cmd: str
    ) -> list[str]:
        """补全命令"""

        completions = ctx.cli_complete.get_completions(
            split_arg_string(cmd),
            ''
        )
        return [str(c.value) for c in completions if c.type == 'plain']

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

    @classmethod
    @wahu_methodize()
    async def cli_open_editor(cls, ctx: WahuContext, name: str) -> None:
        """在编辑器中打开"""

        for cs in ctx.cli_scripts:
            if cs.name == name:
                webbrowser.open(str(cs.path))
                break
        else:
            raise WahuRuntimeError(f'找不到 CliScript {name}')
