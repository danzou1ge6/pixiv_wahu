from typing import TYPE_CHECKING
import click

from wahu_backend.wahu_methods import WahuMethods


if TYPE_CHECKING:
    from wahu_backend.wahu_core import CliClickCtxObj

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap


NAME = '重新加载命令行脚本'
DESCRIPTION = '从 `config.cli_script_dir` 重新加载命令行脚本'



def mount(wexe: click.Group):

    @wexe.command()
    @wahu_cli_wrap
    async def reload_cli(cctx: click.Context):
        """重新加载命令行脚本
        """

        obj: 'CliClickCtxObj' = cctx.obj

        await WahuMethods.cli_reload(obj.wctx)
