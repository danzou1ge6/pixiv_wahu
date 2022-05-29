import click

from wahu_backend.wahu_core.wahu_cli_helper import wahu_cli_wrap

NAME = '插画数据库操作'
DESCRIPTION = '一些对插画数据库的操作'

_WAHU = '''/\\ \\  __/\\ \\          /\\ \\             /\\ \\
\\ \\ \\/\\ \\ \\ \\     __  \\ \\ \\___   __  __\\ \\ \\
 \\ \\ \\ \\ \\ \\ \\  /'__`\\ \\ \\  _ `\\/\\ \\/\\ \\\\ \\ \\
  \\ \\ \\_/ \\_\\ \\/\\ \\L\\.\\_\\ \\ \\ \\ \\ \\ \\_\\ \\\\ \\_\\
   \\ `\\___x___/\\ \\__/.\\_\\\\ \\_\\ \\_\\ \\____/ \\/\\_\\
    '\\/__//__/  \\/__/\\/_/ \\/_/\\/_/\\/___/   \\/_/'''

def mount(wexe: click.Group):

    @wexe.command()
    @wahu_cli_wrap
    async def wahu(wctx):
        """Wahu!"""
        wctx.obj.pipe.putline(_WAHU)
