import click

from wahu_backend.wahu_core.wahu_cli_util import wahu_cli_wrap
from wahu_backend.constants import lazyimageURL

NAME = '打印 Wahu'
DESCRIPTION = 'Wahu!'

_WAHU = '''/\\ \\  __/\\ \\          /\\ \\             /\\ \\
\\ \\ \\/\\ \\ \\ \\     __  \\ \\ \\___   __  __\\ \\ \\
 \\ \\ \\ \\ \\ \\ \\  /'__`\\ \\ \\  _ `\\/\\ \\/\\ \\\\ \\ \\
  \\ \\ \\_/ \\_\\ \\/\\ \\L\\.\\_\\ \\ \\ \\ \\ \\ \\_\\ \\\\ \\_\\
   \\ `\\___x___/\\ \\__/.\\_\\\\ \\_\\ \\_\\ \\____/ \\/\\_\\
    '\\/__//__/  \\/__/\\/_/ \\/_/\\/_/\\/___/   \\/_/'''

def mount(wexe: click.Group):

    @wexe.command()
    @click.option('--image', '-i', is_flag=True)
    @wahu_cli_wrap
    async def wahu(wctx, image: bool):
        """Wahu!
        """
        if image:
            wctx.obj.pipe.put(src=lazyimageURL)
        else:
            wctx.obj.pipe.putline(_WAHU)
