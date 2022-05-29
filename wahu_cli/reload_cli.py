from typing import TYPE_CHECKING
import click


if TYPE_CHECKING:
    from wahu_backend.wahu_methods.cli import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_helper import wahu_cli_wrap


NAME = '重新加载命令行脚本'
DESCRIPTION = '从 `config.cli_script_dir` 重新加载命令行脚本'



def mount(wexe: click.Group):

    @wexe.command()
    @wahu_cli_wrap
    async def reload_cli(cctx: click.Context):
        """重新加载命令行脚本
        """

        obj: 'CliClickCtxObj' = cctx.obj
        wctx, pipe, wmethods = obj.unpkg()

        await wmethods.cli_reload.f(wmethods, wctx)
